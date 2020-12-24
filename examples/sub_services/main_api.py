"""
Example API that receives requests from the internet and delegates work to
subservices
"""
import requests
from fastapi import FastAPI, status as http_status
from .service_util import *

app = FastAPI()


# Todo: find the workers and their status
WORKERS = {'signed': 'http://127.0.0.1:8001',
           'unsigned': 'http://127.0.0.1:8002'}


@app.get('/health')
async def health():
    return {}


@app.post('/query',
          status_code=http_status.HTTP_202_ACCEPTED,
          response_model=JobStatus)
def query(search_query: NetworkSearchQuery):
    # Decide which service the query should run to
    if search_query.signed is None:
        # query unsigned worker
        status = requests.post(WORKERS['unsigned'], json=search_query.json())
    else:
        # Query signed worker
        status = requests.post(WORKERS['signed'], json=search_query.json())

    return status
