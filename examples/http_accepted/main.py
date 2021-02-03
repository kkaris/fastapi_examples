"""
Create a webservice where the client does some polling of the server until
the server is done with its task

In this case we'll be following this structure:
1. Server gets a job request, returns an ID with a 202 ACCEPTED status code
   and puts the job in the queue <-- DONE
2. Client polls "<location>" until 200 is returned (could poll S3?) OR polls
   polling endpoint on
3. Service moves on to the next job in line

Todo:
 - META: create remote on your github
 - Re-create the polling endpoint by using multiprocessing global variables:
   https://stackoverflow.com/questions/30333591/
   python-3-global-variables-with-asyncio-apscheduler
   https://docs.python.org/3.7/library/asyncio-sync.html#asyncio-sync
   OR
   Work around threading by having the polling endpoint check if the
   resulting file is available or not
   OR
   maybe the "polling problem" of shared variables and having the polling
   endpoint accessing them is solved by the python asyncio-queue (see below)
 - Create an actual job queue:
   https://docs.python.org/3/library/
   asyncio-queue.html#asyncio-example-queue-dist
   https://testdriven.io/blog/developing-an-asynchronous-task-queue-in-python/
   https://realpython.com/async-io-python/#using-a-queue
   OR
   Celery:
   https://docs.celeryproject.org/en/stable/

Try with:
res = requests.post('http://127.0.0.1:8000/submit_job', json=<VALID JSON>)
job_id = str(res.json()['id']) if res.status_code in [200, 202] else \
    res.status_code; print(job_id)
res = requests.get(f'http://127.0.0.1:8000/data/{job_id}_result.json')
n = 1
while res.status_code != 200:
    print(f'Got status {res.status_code}, waiting for {n} seconds')
    sleep(n)
    res = requests.get(f'http://127.0.0.1:8000/data/{job_id}_result.json')
    n *= 2
print(res.json())

Example output:
Got status 404, waiting for 1 seconds
Got status 404, waiting for 2 seconds
Got status 404, waiting for 4 seconds
{'result_text': 'path found', 'number_of_paths': 10, 'source': 'IRAK3',
'target': 'EGFR'}


As always, run with
> uvicorn module.file:app --reload
"""
import json
import asyncio
import logging

from random import randint
from typing import Tuple, Optional
from pathlib import Path
from fastapi import FastAPI, status as http_status, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from indra_network_search.util import NetworkSearchQuery

app = FastAPI()
HERE = Path(__file__).parent
DATA_DIR = HERE.parent.absolute().joinpath('data')
print(f'DATA_DIR={DATA_DIR}')
print(f'DATA_DIR={DATA_DIR.absolute().as_posix()}')
app.mount('/data', StaticFiles(directory=DATA_DIR.absolute().as_posix()),
          name='data')
logger = logging.getLogger(__name__)

queues = dict(
    pending={},
    working={},
    finished={}
)


class PollReq(BaseModel):
    """Polling request body"""
    job_id: str


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
    fname: str = None
    location: str = None

    def get_fname(self):
        """Get the file name for the query"""
        # Create file name
        if self.location is None:
            self.set_location()
        return self.fname

    def _set_fname(self):
        self.fname = f'{self.query.get_hash()}_result.json'

    def set_location(self):
        """Set self.location"""
        # Initialize fname
        if self.fname is None:
            self._set_fname()
        # Set job.location
        self.location = f'/data/{self.fname}'


class JobStatusException(Exception):
    """Raise when a job status could not be updated"""


def get_work_status(job_id: str) -> Tuple[Optional[JobStatus], str]:
    """Check the status of a job"""
    logger.info(f'Looking for job {job_id}')
    for q in ['finished', 'working', 'pending']:
        for query_hash, job in queues[q].items():
            if query_hash == job_id:
                logger.info(f'Found job {job_id} in queue "{q}"')
                return job, q
    logger.info(f'Job {job_id} was not found in any queue')
    return None, 'no_such_job'


def update_job_status(qh: str, from_status: str, to_status: str):
    """Update the job status from from_status to to_status"""
    logger.info(f'Updating job {qh} from {from_status} to {to_status}')
    try:
        job = queues[from_status].pop(qh)
        assert job is not None
        job.status = to_status
        queues[to_status][qh] = job
    except AssertionError:
        raise JobStatusException(f'Could not find job {qh} in queue')


def add_job(job: JobStatus):
    """Add a job to the queue"""
    job.status = 'pending'
    qh = job.query.get_hash()
    queues['pending'][qh] = job
    logger.info(f'Added job {qh} to {job.status}')


async def crunch_the_numbers(q: NetworkSearchQuery):
    """Function representing some CPU heavy task

    Put results on a Result model
    Set result to Result
    Set location to URL
    """
    q_hash = q.get_hash()
    logger.info(f'Crunching numbers for job {q_hash}')
    # Update job status to 'working', check we actually got a job
    update_job_status(q_hash, 'pending', 'working')
    job, status = get_work_status(q_hash)
    await asyncio.sleep(randint(2, 30))
    # Create Result object
    res = Result(result_text='path found', number_of_paths=10,
                 source=q.source, target=q.target)
    logger.info(f'Finished on job {q_hash}')
    # Update job.result
    job.result = res
    # Get file name. This also set job.location
    fname = job.get_fname()
    with DATA_DIR.joinpath(fname).open('w') as f:
        logger.info(f'Writing results to {DATA_DIR.joinpath(fname)}')
        json.dump(fp=f, obj=job.dict())
    # Update job status to 'finished', check we actually got a job
    update_job_status(q_hash, 'working', 'finished')
    logger.info(f'Results served at {job.location}')
    logger.info(f'Job {q_hash} terminated successfully')


@app.post('/submit_job', status_code=http_status.HTTP_202_ACCEPTED,
          response_model=JobStatus)
def submit_job(nsq: NetworkSearchQuery,
               background_tasks: BackgroundTasks):
    """Handles job submissions"""
    # Get query hash
    query_hash = nsq.get_hash()
    # Create new JobStatus object
    logger.info(f'Creating new job: {query_hash}')
    job = JobStatus(id=query_hash, status='pending', query=nsq)
    job.set_location()
    # Add job
    add_job(job)
    # Add job to background process
    logger.info(f'Sent job {query_hash} to run in background')
    background_tasks.add_task(crunch_the_numbers, nsq)
    # Return job status
    return job
