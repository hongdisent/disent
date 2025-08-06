library(shiny)
library(bslib)
library(dplyr)
library(ggplot2)
library(ggExtra)
library(readr)

# Load penguins dataset
penguins_url <- "https://raw.githubusercontent.com/jcheng5/simplepenguins.R/main/penguins.csv"
df <- read_csv(penguins_url)

# Select numeric variables for plotting
df_num <- df |> select(where(is.numeric), -Year)

# UI
ui <- page_sidebar(
  title = "Explore the Penguins Dataset",

  sidebar = sidebar(
    varSelectInput("xvar", "Choose X-axis", df_num, selected = "Bill Length (mm)"),
    varSelectInput("yvar", "Choose Y-axis", df_num, selected = "Bill Depth (mm)"),
    
    checkboxGroupInput(
      "species", "Select Species",
      choices = unique(df$Species),
      selected = unique(df$Species)
    ),
    hr(),
    checkboxInput("color_by_species", "Color by Species", TRUE),
    checkboxInput("show_marginals", "Show Marginal Distributions", TRUE),
    
    radioButtons("plot_type", "Choose Plot Type",
                 choices = c("Scatter" = "scatter",
                             "Violin (X ~ Species)" = "violin_x",
                             "Violin (Y ~ Species)" = "violin_y",
                             "Boxplot (X ~ Species)" = "box_x",
                             "Boxplot (Y ~ Species)" = "box_y"),
                 selected = "scatter")
  ),

  plotOutput("main_plot")
)

# Server
server <- function(input, output, session) {
  filtered_data <- reactive({
    req(input$species)
    df |> filter(Species %in% input$species)
  })

  output$main_plot <- renderPlot({
    data <- filtered_data()
    x <- input$xvar
    y <- input$yvar
    species_col <- if (input$color_by_species) aes(color = Species) else NULL

    # Choose plot type
    if (input$plot_type == "scatter") {
      p <- ggplot(data, aes(!!x, !!y)) +
        geom_point(species_col) +
        theme_minimal() +
        theme(legend.position = "bottom")

      if (input$show_marginals) {
        p <- ggMarginal(p, type = "density", margins = "both",
                        groupColour = input$color_by_species,
                        groupFill = input$color_by_species)
      }

    } else if (input$plot_type == "violin_x") {
      p <- ggplot(data, aes(x = Species, y = !!x, fill = Species)) +
        geom_violin(trim = FALSE) +
        theme_minimal()

    } else if (input$plot_type == "violin_y") {
      p <- ggplot(data, aes(x = Species, y = !!y, fill = Species)) +
        geom_violin(trim = FALSE) +
        theme_minimal()

    } else if (input$plot_type == "box_x") {
      p <- ggplot(data, aes(x = Species, y = !!x, fill = Species)) +
        geom_boxplot() +
        theme_minimal()

    } else if (input$plot_type == "box_y") {
      p <- ggplot(data, aes(x = Species, y = !!y, fill = Species)) +
        geom_boxplot() +
        theme_minimal()
    }

    p
  }, res = 100)
}

shinyApp(ui, server)
