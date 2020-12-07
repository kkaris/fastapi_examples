"""
Create a webservice where the client does some polling of the server until
the server is done with its task

In this case we'll be following this structure:
1. Server gets a job request, returns an ID with a 202 ACCEPTED status code
   and puts the job in the queue
2. Client polls server (in the future, client could poll a different service
   than this one, e.g. other FastAPI service or AWS S3) until a response
   with "job done, find result here <link>" is returned
3. Service moves on to the next job in line
"""
import asyncio
from pathlib import Path
from fastapi import FastAPI, status, BackgroundTasks
from pydantic import BaseModel
from collections import deque
from random import randint
from indra_depmap_service.util import NetworkSearchQuery

app = FastAPI()
HERE = Path(__file__).parent
DATA_DIR = HERE.parent.parent.joinpath('data')

queues = dict(
    pending=deque(),
    working=deque(),
    finished=deque()
)


class PollReq(BaseModel):
    """Polling request body"""
    id: str


def get_work_status(job_id: str):
    """Check the status of a job"""
    for q in ['finished', 'working', 'pending']:
        for job in queues[q]:
            if str(job['id']) == job_id:
                return job, q


async def crunch_the_numbers(q: NetworkSearchQuery):
    """Function representing some CPU heavy task"""
    res = {'result': 'path found',
           'number_of_path': 10,
           'source': q.source,
           'target': q.target}
    await asyncio.sleep(randint(1, 30))
    return res


def create_job(background_tasks: BackgroundTasks, query: NetworkSearchQuery):
    """Function that creates a job that is run in the background"""
    qh = query.get_hash()
    background_tasks.add_task(crunch_the_numbers, query)
    queues['pending'].append(qh)
    return qh


@app.post('/poll')
async def poll(pq: PollReq):
    location, job_status = get_work_status(pq.id)
    resp = {'id': pq.id,
            'status': job_status}
    if location:
        resp['location'] = location
    return resp


@app.post('/status/{id}')
async def get_job_status(id: str):
    job, job_status = get_work_status(id)

# todo create query receiver that submits a job
