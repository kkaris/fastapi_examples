"""
This examples shows:
1. How to use queues
2. How to use asyncio queues specifically
3. How to asynchronously poll a "work in progress"
"""
from fastapi import FastAPI, Query
import asyncio
from asyncio.queues import Queue

app = FastAPI()
