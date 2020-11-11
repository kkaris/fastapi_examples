from fastapi import FastAPI
from typing import List, Set, Tuple, Dict

app = FastAPI()


@app.get('/')
async def root():
    return {'message': 'Hello World'}


@app.post('/items/{item_id}')
async def read_item(item_id: int):
    return {'item_id': item_id}


def list_func(items: List[str]):
    print(', '.join(items))
    for item in items:
        print(item.capitalize())


def tuple_set_func(tuple_items: Tuple[int, str], set_items: Set[bytes]):
    return tuple_items, set_items


def dict_func(prices: Dict[str, float], ):
    for item, price in prices.items():
        print(item.capitalize(), str(price))
