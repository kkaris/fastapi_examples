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
from time import sleep
from typing import Optional
from pathlib import Path
from logging import getLogger
from fastapi import BackgroundTasks, FastAPI, Depends
# from .service_util import QueryBodySum
from .service_util import WriteToLogQuery

app = FastAPI()

logger = getLogger(__name__)
HERE = Path(__file__).parent
LOGFILE = HERE.joinpath('log.txt')


def write_to_log(message: str):
    logger.info(f'Writing {message} to file {str(LOGFILE)}')
    sleep(5)
    with LOGFILE.open('a') as f:
        f.write(message)
    logger.info('Finished writing to logfile')


def get_query(background_tasks: BackgroundTasks, q: Optional[str] = None):
    if q:
        message = f'Found query {q}\n'
        background_tasks.add_task(write_to_log, message)
    return q


@app.post('/write-to-log')
async def summation(query_params: WriteToLogQuery,
                    background_tasks: BackgroundTasks,
                    q: str = Depends(get_query)):
    """Example of endpoint doing queries in the background

    email: str
        Who to send an email to
    background_tasks: BackgroundTasks

    Returns
    -------
    Dict
        Json of status
    """
    log = f'Message to {query_params.address}: {query_params.message} {q}\n'
    background_tasks.add_task(write_to_log, log)
    return {'message': 'Message written in background'}
