"""
Example API that receives requests from the internet and delegates work to
subservices
"""
import logging
from pathlib import Path

import requests
from typing import Optional
from requests.exceptions import ConnectionError
from fastapi import FastAPI, status as http_status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from . import *

logger = logging.getLogger(__name__)
app = FastAPI()

app.mount('/data', StaticFiles(directory=FASTAPI_DATA_DIR.as_posix()),
          name='data')

STATUS = ServiceStatus(service_type=WORKER_ROLE, status='booting')
HEALTH: Optional[HealthStatus] = None


def _set_health_status():
    # Todo: run async when you get a grip on aiohttp
    global HEALTH
    try:
        res = requests.get(f'{SERVICE_URLS["unsigned"]}/health')
        unsigned_health = res.json().get('status', 'offline') if \
            res.status_code == 200 else 'offline'
    except (ConnectionError, AttributeError):
        unsigned_health = 'offline'
    try:
        res = requests.get(f'{SERVICE_URLS["signed"]}/health')
        signed_health = res.json().get('status', 'offline') if \
            res.status_code == 200 else 'offline'
    except (ConnectionError, AttributeError):
        signed_health = 'offline'

    HEALTH = HealthStatus(unsigned_service=unsigned_health,
                          signed_service=signed_health,
                          public_api=STATUS.status)


@app.get('/public_health', response_model=ServiceStatus)
async def public_health():
    """Returns health of this service only"""
    return STATUS


@app.get('/health', response_model=HealthStatus)
def health():
    """Returns health of this service and the workers"""
    _set_health_status()  # Run async when updated to async
    return HEALTH


@app.post('/query',
          status_code=http_status.HTTP_202_ACCEPTED,
          response_model=JobStatus)
def query(search_query: NetworkSearchQuery):
    """Query the service and relay to correct worker"""
    # Decide which service the query should run to, the workers should
    # respond with 202 after sending the job to the background
    logger.info(f'Got networksearchquery: {search_query.dict()}')
    if search_query.sign == 'no_sign' or search_query.sign is None:
        # query unsigned worker
        res = requests.post(f'{SERVICE_URLS["unsigned"]}/query',
                            json=search_query.dict())
    else:
        # Query signed worker
        res = requests.post(f'{SERVICE_URLS["signed"]}/query',
                            json=search_query.dict())

    if res.status_code == 202:
        return JobStatus(**res.json())
    else:
        logger.warning(f'Query responded with status code {res.status_code}')
        return JSONResponse(status_code=res.status_code,
                            content=EMPTY_JOB_STATUS.dict())


# Change to 'online' after everything is loaded
STATUS.status = 'online'
