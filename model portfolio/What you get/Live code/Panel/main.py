import panel as pn

from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier

pn.extension(sizing_mode="stretch_width", design='material', template="fast")

pn.state.template.param.update(
    title="🌿 Interactive XGBoost Classifier: Iris Dataset"
)

st_description = """
### Explore XGBoost on Iris Data

This interactive app trains an **XGBoost classifier** on the classic **Iris dataset** using adjustable hyperparameters:
- `Number of Trees` (`n_estimators`)
- `Maximum Tree Depth`
- `Booster Type` (`gbtree`, `gblinear`, or `dart`)

🔁 Change the sliders and dropdown to see how model accuracy responds in real-time.
"""

pn.Column(st_description).servable()


iris_df = load_iris(as_frame=True)

n_trees = pn.widgets.IntSlider(start=2, end=30, name="Number of trees")
max_depth = pn.widgets.IntSlider(start=1, end=10, value=2, name="Maximum Depth") 
booster = pn.widgets.Select(options=['gbtree', 'gblinear', 'dart'], name="Booster")

def pipeline(n_trees, max_depth, booster):
    model = XGBClassifier(max_depth=max_depth, n_estimators=n_trees, booster=booster)
    model.fit(iris_df.data, iris_df.target)
    accuracy = round(accuracy_score(iris_df.target, model.predict(iris_df.data)) * 100, 1)
    return pn.indicators.Number(
        name=f"Test score",
        value=accuracy,
        format="{value}%",
        colors=[(97.5, "red"), (99.0, "orange"), (100, "green")],
        align='center'
    )

pn.Row(
    pn.Column(booster, n_trees, max_depth, width=320).servable(area='sidebar'),
    pn.Column(
        "Simple example of training an XGBoost classification model on the small Iris dataset.",
        iris_df.data.head(),
        
        "Adjust the hyperparameters to re-run the XGBoost classifier. The training accuracy score will adjust accordingly:",
        pn.bind(pipeline, n_trees, max_depth, booster),
        pn.bind(lambda n_trees, max_depth, booster: f'# <code>{n_trees=}, {max_depth=}, {booster=}</code>', n_trees, max_depth, booster),
    ).servable(),
)