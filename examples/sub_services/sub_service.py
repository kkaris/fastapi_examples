"""
Handles some requests from the main api
Requests that could take a long time (like weighted path searches) are done
as background tasks

Run this as a server using uvicorn with:
> uvicorn sub_services.sub_service:app --reload

Test with requests
res = requests.post('http://127.0.0.1:8000/write-to-log?q=1234567890abcdef',
    json={'address': 'my@email.com', 'message': 'Hello FastAPI!'})

"""
import asyncio
from time import sleep
from numpy.random import exponential as rnd_exp
from logging import getLogger
from fastapi import BackgroundTasks, FastAPI, status as http_status
from .service_util import *

app = FastAPI()

logger = getLogger(__name__)

# Initialize with 'booting' before we're done loading stuff
STATUS = ServiceStatus(service_type='signed worker',
                       status='booting')

edge1: Edge = Edge(hashes=[123456789, 987654321],
                   sources={'reach': 5, 'xdd': 3, 'tas': 2})
edge2: Edge = Edge(hashes=[-123456789, -987654321],
                   sources={'sparser': 5, 'tas': 3})
edge3: Edge = Edge(hashes=[-192837465, 9081726354],
                   sources={'tas': 1, 'drugbank': 1})


def handle_query(nsq: NetworkSearchQuery, job_status: JobStatus):
    """Simulate high work intensity with a sleep

    Todo: run some CPU heavy loop doing nonsense to test the robustness
    """
    # Update job status to 'working'
    job_status.status = 'working'
    upload_json(job_status)

    pr = PathResult(one_edge=[edge1], two_edge=[edge2, edge3])
    st = [edge1, edge2]
    qr = QueryResult(forward_paths=pr, shared_targets=st)
    qr.fname = f'{nsq.get_hash()}_result.json'

    # Simulate work that often takes less than one or a couple of seconds,
    # but sometimes takes a lot longer
    sleep_time = rnd_exp(scale=7)
    logger.info(f'Sleeping for {sleep_time}')
    sleep(sleep_time)

    # Upload results
    upload_json(qr)

    # Update job status
    job_status.status = 'done'
    upload_json(job_status)


@app.get('/health', response_model=ServiceStatus)
async def health():
    """Health endpoint"""
    return STATUS


# This is where to make the decision if we should run network search in the
# background or if we should run a blocking query
# Try background for now
@app.post('/query',
          status_code=http_status.HTTP_202_ACCEPTED,
          response_model=JobStatus)
async def query(search_query: NetworkSearchQuery,
                bgt: BackgroundTasks):
    """Runs a query and uploads status and potential results"""
    logger.info(f'Handling query {search_query.get_hash()}')
    meta_name = f'{search_query.get_hash()}_meta.json'
    meta_loc = f'/data/{meta_name}'
    job_status = JobStatus(id=search_query.get_hash(),
                           status='pending',
                           fname=meta_name,
                           location=meta_loc)
    bgt.add_task(upload_json, job_status)
    bgt.add_task(handle_query, search_query, job_status)
    return job_status


# Change to 'online' after everything is loaded
# Simulate some io heavy loading with asyncio.sleep e.g. loading indra graphs
asyncio.sleep(5)
STATUS.status = 'online'
