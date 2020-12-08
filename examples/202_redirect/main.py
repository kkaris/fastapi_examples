"""
Create a webservice where the client does some polling of the server until
the server is done with its task

In this case we'll be following this structure:
1. Server gets a job request, returns an ID with a 202 ACCEPTED status code
   and puts the job in the queue
2. Client polls server until a response with "job done, find result here
   <link>" is returned (in the future, client could poll a different service
   than this one, e.g. other FastAPI service or AWS S3)
3. Service moves on to the next job in line

Todo:
 - Serve results as static json files:
   https://fastapi.tiangolo.com/tutorial/static-files/
 - Use deque to "simulate" actual job queue instead. Requires some type of
   event handling/while loop to "run until no more jobs", where submitted
   jobs are either started immediately if the server state is "awaiting
   jobs" or put in the queue if the server state is "working".
   https://testdriven.io/blog/developing-an-asynchronous-task-queue-in-python/
"""
import json
import asyncio
import logging
from typing import Tuple, Optional
from pathlib import Path
from fastapi import FastAPI, status as http_status, BackgroundTasks
from pydantic import BaseModel
from collections import deque
from random import randint
from indra_depmap_service.util import NetworkSearchQuery

app = FastAPI()
HERE = Path(__file__).parent
DATA_DIR = HERE.parent.parent.joinpath('data')
logger = logging.getLogger(__name__)

queues = dict(
    pending={},
    working={},
    finished={}
)


class PollReq(BaseModel):
    """Polling request body"""
    id: str


class Result(BaseModel):
    """Result model"""
    result_text: str
    number_of_paths: int
    source: str
    target: str


class JobStatus(BaseModel):
    """JobStatus model"""
    status: str
    id: str
    query: NetworkSearchQuery
    result: Result = None
    location: str = None


class JobStatusException(Exception):
    """Raise when a job status could not be updated"""


def get_work_status(job_id: str) -> Tuple[Optional[JobStatus], str]:
    """Check the status of a job"""
    for q in ['finished', 'working', 'pending']:
        for query_hash, job in queues[q]:
            if query_hash == job_id:
                return job, q
    return None, 'no_such_job'


def update_job_status(qh: str, from_status: str, to_status: str):
    try:
        job = queues[from_status].pop(qh)
        assert job is not None
        job.status = to_status
        queues[to_status][qh] = job
    except AssertionError:
        raise JobStatusException(f'Could not find job {qh} in queue')


def add_job(job: JobStatus):
    job.status = 'pending'
    queues['pending'][job.query.get_hash()] = job


async def crunch_the_numbers(q: NetworkSearchQuery):
    """Function representing some CPU heavy task

    Put results on a Result model
    Set result to Result
    Set location to URL
    """
    q_hash = q.get_hash()
    # Update job status to 'working', check we actually got a job
    update_job_status(q_hash, 'pending', 'working')
    job, status = get_work_status(q_hash)
    await asyncio.sleep(randint(1, 30))
    # Create Result object
    res = Result(result_text='path found', number_of_paths=10,
                 source=q.source, target=q.target)
    # Update job.result
    job.result = res
    # Write result to file
    fname = f'{q_hash}_result.json'
    with DATA_DIR.joinpath(fname).open() as f:
        json.dump(fp=f, obj=res.dict())
    # Update job.location
    job.location = f'/data/{fname}'
    # Update job status to 'finished', check we actually got a job
    await update_job_status(q_hash, 'working', 'finished')


@app.post('/poll', response_model=JobStatus)
async def poll(pq: PollReq):
    logger.info(f'Got poll request for job {pq.id}')
    job_status, queue = get_work_status(pq.id)
    logger.info(f'Job found has status {queue}')
    return job_status


@app.post('/submit_job', status_code=http_status.HTTP_202_ACCEPTED,
          response_model=JobStatus)
async def submit_job(nsq: NetworkSearchQuery,
                     background_tasks: BackgroundTasks):
    # Get query hash
    query_hash = nsq.get_hash()
    # Create new JobStatus object
    job = JobStatus(id=query_hash, status='pending', query=nsq)
    # Add job to background process
    background_tasks.add_task(crunch_the_numbers, nsq)
    # Return job status
    return job
