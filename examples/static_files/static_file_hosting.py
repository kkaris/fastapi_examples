"""
Example of providing static files

File will exist at:
http://localhost:8000/data/3809006135_query.json

As always, run with
> uvicorn module.file:app --reload
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

DATA_DIR = Path(__file__).parent.joinpath('data')
print(f'DATA_DIR={DATA_DIR.absolute().as_posix()}')

app = FastAPI()

app.mount('/data', StaticFiles(directory=DATA_DIR.absolute().as_posix()),
          name='data')
