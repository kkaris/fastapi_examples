"""
Example API that receives requests from the internet and delegates work to
subservices
"""
import logging
from pathlib import Path

import requests
from fastapi import FastAPI, status as http_status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .service_util import *
from . import DATA_DIR

logger = logging.getLogger(__name__)
app = FastAPI()

app.mount('/data', StaticFiles(directory=DATA_DIR.as_posix()), name='data')

# Todo: find the workers and their status
WORKERS = {'signed': 'http://127.0.0.1:8001',
           'unsigned': 'http://127.0.0.1:8002'}


STATUS = ServiceStatus(service_type='public api', status='booting')


@app.get('/public_health', response_model=ServiceStatus)
async def public_health():
    """Returns health of this service only"""
    return STATUS


@app.get('/health', response_model=HealthStatus)
def health():
    """Returns health of this service and the workers"""
    # Todo: poll the workers for their status, do so asynchronously when you
    #  get a grip on aiohttp
    unsigned_health = requests.get(f'{WORKERS["unsigned"]}/health').json()
    signed_health = requests.get(f'{WORKERS["signed"]}/health').json()
    hs = HealthStatus(unsigned_service=unsigned_health['status'],
                      signed_service=signed_health['stats'],
                      public_api=STATUS.status)
    return hs


@app.post('/query',
          status_code=http_status.HTTP_202_ACCEPTED,
          response_model=JobStatus)
def query(search_query: NetworkSearchQuery):
    """Query the service and relay to correct worker"""
    # Decide which service the query should run to, the workers should
    # respond with 202 after sending the job to the background
    if search_query.signed is None:
        # query unsigned worker
        res = requests.post(WORKERS['unsigned'],
                            json=search_query.json())
    else:
        # Query signed worker
        res = requests.post(f'{WORKERS["signed"]}/query',
                            json=search_query.json())

    if res.status_code == 202:
        return JobStatus(**res.json())
    else:
        logger.warning(f'Query responded with status code {res.status_code}')
        return JSONResponse(status_code=res.status_code,
                            content=EMPTY_JOB_STATUS)


# Change to 'online' after everything is loaded
STATUS.status = 'online'
