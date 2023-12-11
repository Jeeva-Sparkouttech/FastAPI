from typing import Union,Annotated,List
from enum import Enum

from fastapi import FastAPI, Query, Path, Body
from pydantic import BaseModel, Field, HttpUrl

app = FastAPI()

# Basic
class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

class User(BaseModel):
    username: str
    full_name: str | None = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/path_parameter/validations/{item_id}")
def read_item(item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    q: str,
    size:float = Query(gt=0, lt=10.5)):
    # *,item_id: int = Path(title="The ID of the item to get"),q: Union[str, None] 
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Item,
    user: User,
    importance: Annotated[int, Body(gt=0)],
    q: str | None = None,
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    if q:
        results.update({"q": q})
    return results


@app.put("/embed/{item_id}")
async def update_item(
    item_id: int,
    item: Annotated[Item,Body(embed = True)],
    q: str | None = None,
):
    return item


#Enum
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


#Query param
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None, short: bool = False) -> dict:
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

#Request body
class SampleItem(BaseModel):
    # name: str = Field(examples=["Foo"])
    name: str 
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: Annotated[float, Field(gt=0, description="The price must be greater than zero")]
    tags: set[str]
    my_list: List[str] = []


@app.post("/request_body/")
# item: Annotated[SampleItem, Body(examples = [{"name": "Foo","description": "A very nice Item","price": 35.4}])]
async def create_item(item:Annotated[SampleItem,Body(
            openapi_examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
                    },
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
            },
        )], user: User, importance : Annotated[int, Body()]):
    # importance : int = Body() or importance : Annotated[int, Body()] singular values in body
    # item: SampleItem | None = None  Optional body param
    return item

#Query Parameters and String Validations (Annotation)
@app.get("/queryparam/validation")
async def read_items(q: Annotated[List[str], Query(alias="item-query",title="Query string",description="Query string for the items to search in the database that have a good match",deprecated=True)] = []):
    # q: Annotated[str | None, Query(min_length=3,max_length=19,pattern="^fixedquery$")] = ... new method using annotated
    # q: Union[str, None] = Query(default=None, max_length=50) old method
    # q: Annotated[str | None, Query(min_length=3,max_length=19,pattern="^fixedquery$")] = ... (ellipsis declare that a value is required)
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

#Nested Models

class Image(BaseModel):
    url: HttpUrl
    name: str


class Nested(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    # image: Image | None = None
    image: list[Image] | None = None
    
    #Extra JSON Schema data in Pydantic models
    # model_config = {
    #     "json_schema_extra": {
    #         "examples": [
    #             {
    #                 "name": "Foo",
    #                 "description": "A very nice Item",
    #                 "price": 35.4,
    #                 "tax": 3.2,
    #             }
    #         ]
    #     }
    # }


@app.put("/nested/model/{item_id}")
async def update_item(item_id: int, item: Nested, image: list[Image], weights: dict[int, float]):
    results = {"item_id": item_id, "item": item}
    return weights

