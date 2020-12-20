"""
This example show how to constrain queries using Query and BaseModel
"""
from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()
