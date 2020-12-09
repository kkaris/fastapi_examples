"""
Example of providing static files

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
