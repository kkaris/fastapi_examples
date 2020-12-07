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
import json
import asyncio
from pathlib import Path
from fastapi import FastAPI, status as http_status, BackgroundTasks
from pydantic import BaseModel
from collections import deque
from random import randint
from indra_depmap_service.util import NetworkSearchQuery

app = FastAPI()
HERE = Path(__file__).parent
DATA_DIR = HERE.parent.parent.joinpath('data')

queues = dict(
    pending={},
    working={},
    finished={}
)


class PollReq(BaseModel):
    """Polling request body"""
    id: str


class JobStatus(BaseModel):
    """JobStatus model"""
    status: str
    id: str
    query: NetworkSearchQuery
    result: str = None
    location: str = None


class JobStatusException(Exception):
    """Raise when a job status could not be updated"""


async def get_work_status(job_id: str):
    """Check the status of a job"""
    for q in ['finished', 'working', 'pending']:
        for query_hash, job in queues[q]:
            if query_hash == job_id:
                return job, q


async def update_job_status(qh: str, from_status: str, to_status: str):
    try:
        job = queues[from_status].pop(qh)
        assert job is not None
        await update_status(job, to_status)
        queues[to_status][qh] = job
    except AssertionError:
        raise JobStatusException(f'Could not find job {qh} in queue')


async def add_job(job: JobStatus):
    # todo add job to queue
    pass


async def update_status(job: JobStatus, to_status: str):
    job.status = to_status


async def crunch_the_numbers(q: NetworkSearchQuery):
    """Function representing some CPU heavy task"""
    q_hash = q.get_hash()
    # Update job status to 'working', check we actually got a job
    await update_job_status(q_hash, 'pending', 'working')
    res = {'result': 'path found',
           'number_of_paths': 10,
           'source': q.source,
           'target': q.target}
    await asyncio.sleep(randint(1, 30))
    # Write to file
    with DATA_DIR.joinpath().open(f'{q_hash}_result.json') as f:
        json.dump(fp=f, obj=res)
    # Update job status to 'finished', check we actually got a job
    await update_job_status(q_hash, 'working', 'finished')


@app.post('/poll')
async def poll(pq: PollReq):
    location, job_status = get_work_status(pq.id)
    resp = {'id': pq.id,
            'status': job_status}
    if location:
        resp['location'] = location
    return resp


@app.post('/submit_job', status_code=http_status.HTTP_202_ACCEPTED,
          response_model=JobStatus)
async def submit_job(nsq: NetworkSearchQuery,
                     background_tasks: BackgroundTasks):
    # Get query hash
    query_hash = nsq.get_hash()
    # Create a dict representing a JobStatus
    job_status = {'id': query_hash, 'status': 'pending', 'query': nsq}
    # Add job to background process
    background_tasks.add_task(crunch_the_numbers, nsq)
    # Update jobqueue
    queues['pending'].append(job_status)
    # Return job status
    return job_status
