from fastapi import FastAPI
from enum import Enum

rates = FastAPI()
users = FastAPI()




class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


app = FastAPI()


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]


"""

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}

"""

"""

# базовые штуки
@rates.get('/')
async def root():
    return {'message': 'Hello World',
            'key2': 'world2'}

@rates.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}



# порядок важен
@users.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@users.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id*2}
    
"""