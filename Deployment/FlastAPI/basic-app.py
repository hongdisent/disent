# Importing Necessary modules
from fastapi import FastAPI
import uvicorn

# Declaring our FastAPI instance
app = FastAPI()

# Defining path operation for root endpoint
@app.get('/')
def main():
    return {'message': 'Welcome to GeeksforGeeks!'}

# Defining path operation for /name endpoint
@app.get('/{name}')
def hello_name(name : str): 
    # Defining a function that takes only string as input and output the
    # following message. 
    return {'message': f'Welcome to GeeksforGeeks!, {name}'}


from sklearn.datasets import load_iris
from sklearn.naive_bayes import GaussianNB

# Loading Iris Dataset
iris = load_iris()

# Getting features and targets from the dataset
X = iris.data
Y = iris.target

# Fitting our Model on the dataset
clf = GaussianNB()
clf.fit(X,Y)

from pydantic import BaseModel

class request_body(BaseModel):
    sepal_length : float
    sepal_width : float
    petal_length : float
    petal_width : float

@app.post('/predict')
def predict(data : request_body):
    test_data = [[
            data.sepal_length, 
            data.sepal_width, 
            data.petal_length, 
            data.petal_width
    ]]
    class_idx = clf.predict(test_data)[0]
    return { 'class' : iris.target_names[class_idx]}