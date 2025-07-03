library(shiny)
library(tidyquant)
library(ggplot2)
library(reshape2)
library(dplyr)

# Load default portfolio
default_portfolio <- data.frame(
  Ticker = c("AAPL", "MSFT", "GOOGL", "AMZN"),
  Weight = c(0.3, 0.3, 0.2, 0.2)
)

# Load Fama-French factors from local CSV (do this once at startup)
load_ff_factors <- function() {
  # Read the CSV file (adjust path if needed)
  ff <- read.csv("F-F_Research_Data_Factors_daily.csv", skip = 3)
  
  # Clean and format the data
  ff %>%
    rename(date = X) %>%
    mutate(date = as.Date(as.character(date), format = "%Y%m%d")) %>%
    filter(!is.na(date)) %>%
    mutate(across(c(Mkt.RF, SMB, HML, RF), ~ as.numeric(as.character(.))/100)) %>%
    rename(Mkt_RF = Mkt.RF) %>%
    select(date, Mkt_RF, SMB, HML, RF)
}

# Load the factors once when the app starts
ff_factors <- load_ff_factors()

ui <- fluidPage(
  titlePanel("Portfolio Analysis Dashboard"),
  
  sidebarLayout(
    sidebarPanel(
      fileInput("file", "Upload Portfolio (CSV)", 
               accept = ".csv",
               placeholder = "Ticker,Weight format"),
      helpText("Default: 30% AAPL, 30% MSFT, 20% GOOGL, 20% AMZN"),
      dateRangeInput("dates", "Date Range:", 
                    start = Sys.Date() - 365, 
                    end = Sys.Date()),
      selectInput("benchmark", "Benchmark:", 
                 choices = c("SPY" = "SPY", "NASDAQ-100" = "QQQ", "Russell 2000" = "IWM"))
    ),
    
    mainPanel(
      tabsetPanel(
        tabPanel("Factor Exposure", plotOutput("factorPlot")),
        tabPanel("Performance", plotOutput("perfPlot")),
        tabPanel("Correlations", plotOutput("corrPlot")),
        tabPanel("Data", tableOutput("portfolioData"))
      )
    )
  )
)

server <- function(input, output) {
  
  # Reactive function to load and process portfolio data
  portfolio_data <- reactive({
    req(input$dates)
    
    if (!is.null(input$file)) {
      df <- tryCatch({
        read.csv(input$file$datapath) %>%
          mutate(Weight = as.numeric(Weight))
      }, error = function(e) {
        showNotification("Error reading file. Using default portfolio.", type = "error")
        default_portfolio
      })
    } else {
      df <- default_portfolio
    }
    
    df$Weight <- df$Weight / sum(df$Weight)
    
    prices <- tryCatch({
      tq_get(df$Ticker, 
             from = input$dates[1], 
             to = input$dates[2],
             get = "stock.prices")
    }, error = function(e) {
      showNotification("Error fetching stock data. Please check tickers or date range.", type = "error")
      NULL
    })
    
    if (is.null(prices)) return(NULL)
    
    returns <- prices %>%
      group_by(symbol) %>%
      tq_transmute(select = adjusted, 
                  mutate_fun = periodReturn, 
                  period = "daily", 
                  col_rename = "returns")
    
    wide_ret <- dcast(returns, date ~ symbol, value.var = "returns")
    wide_ret <- na.omit(wide_ret)
    
    weights <- df$Weight[match(colnames(wide_ret)[-1], df$Ticker)]
    wide_ret$portfolio <- as.matrix(wide_ret[, -1]) %*% weights
    
    list(data = wide_ret, 
         tickers = df$Ticker, 
         weights = weights,
         portfolio = df)
  })
  
  # Use the pre-loaded Fama-French factors
  ff_data <- reactive({
    req(input$dates)
    ff_factors %>%
      filter(date >= input$dates[1] & date <= input$dates[2])
  })
  
  output$factorPlot <- renderPlot({
    port <- portfolio_data()
    ff <- ff_data()
    
    if (is.null(port) || nrow(ff) == 0) {
      showNotification("Not enough data for factor analysis.", type = "warning")
      return(NULL)
    }
    
    merged <- merge(
      data.frame(date = port$data$date, 
                portfolio_return = port$data$portfolio),
      ff,
      by = "date"
    ) %>% 
      mutate(excess_return = portfolio_return - RF)
    
    model <- lm(excess_return ~ Mkt_RF + SMB + HML, data = merged)
    coefs <- coef(model)[-1]
    
    ggplot(data.frame(Factor = names(coefs), Beta = coefs), 
           aes(x = Factor, y = Beta, fill = Factor)) +
      geom_bar(stat = "identity") +
      geom_text(aes(label = round(Beta, 3)), vjust = -0.3) +
      labs(title = "Factor Exposures (Fama-French 3-Factor Model)",
           y = "Beta Coefficient") +
      theme_minimal() +
      theme(legend.position = "none")
  })
  
  # Performance plot
  output$perfPlot <- renderPlot({
    port <- portfolio_data()
    if (is.null(port)) return(NULL)
    
    bench <- tq_get(input$benchmark, 
                   from = input$dates[1], 
                   to = input$dates[2]) %>%
      tq_transmute(select = adjusted, 
                  mutate_fun = periodReturn, 
                  period = "daily")
    
    perf_data <- bind_rows(
      data.frame(
        date = port$data$date,
        Return = cumprod(1 + port$data$portfolio),
        Type = "Portfolio"
      ),
      data.frame(
        date = bench$date,
        Return = cumprod(1 + bench$daily.returns),
        Type = input$benchmark
      )
    )
    
    ggplot(perf_data, aes(x = date, y = Return, color = Type)) +
      geom_line(size = 1) +
      labs(title = "Performance Comparison", y = "Cumulative Return") +
      theme_minimal()
  })
  
  # Correlation heatmap
  output$corrPlot <- renderPlot({
    req(portfolio_data())
    
    cor_data <- portfolio_data()$data[, -ncol(portfolio_data()$data)]  # remove portfolio column
    
    cor_matrix <- cor(cor_data[, -1])  # remove date column
    melted <- melt(cor_matrix)
    
    ggplot(melted, aes(Var1, Var2, fill = value)) +
      geom_tile(color = "white") +
      scale_fill_gradient2(low = "blue", high = "red", mid = "white", 
                          midpoint = 0, limit = c(-1,1), space = "Lab") +
      geom_text(aes(label = round(value, 2)), color = "black", size = 4) +
      theme_minimal() +
      labs(title = "Stock Return Correlations",
           x = "",
           y = "",
           fill = "Correlation") +
      theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust = 1))
  })
  
  # Portfolio data table
  output$portfolioData <- renderTable({
    req(portfolio_data())
    
    data.frame(
      Ticker = portfolio_data()$portfolio$Ticker,
      Weight = paste0(round(portfolio_data()$portfolio$Weight * 100, 1), "%")
    )
  }, striped = TRUE, hover = TRUE)
  # ... [keep the rest of your server code the same] ...
}

shinyApp(ui = ui, server = server)