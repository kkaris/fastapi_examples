"""
Handles some requests from the main api
Requests that could take a long time (like weighted path searches) are done
as background tasks

Run this as a server using uvicorn with:
> uvicorn sub_services.sub_service:app --reload

todo: Try out dependency-injection next
 https://fastapi.tiangolo.com/tutorial/background-tasks/#dependency-injection
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
        message = f'Found query {q}'
        background_tasks.add_task(write_to_log, message)
    return q


@app.post('/write-to-log')
async def summation(email: WriteToLogQuery,
                    background_tasks: BackgroundTasks):
    """Example of endpoint doing queries in the background

    email: str
        Who to send an email to
    background_tasks: BackgroundTasks

    Returns
    -------
    Dict
        Json of status
    """
    try:
        log = f'Message to {email.address}: {email.message}\n'
        background_tasks.add_task(write_to_log, log)
        return {'message': 'Message written in background'}
    except Exception as exc:
        return {'message': f'Something went wrong: {str(exc)}'}
