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
    # Decide which service the query should run to
    if search_query.signed is None:
        # query unsigned worker
        status = requests.post(WORKERS['unsigned'], json=search_query.json())
    else:
        # Query signed worker
        status = requests.post(WORKERS['signed'], json=search_query.json())


# Change to 'online' after everything is loaded
STATUS.status = 'online'
