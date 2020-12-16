"""
Show how to run a task in the background without the server being
unresponsive while the task is performed.

The example show how background tasks can be done in two ways:
1. Explicitly through adding a background task using BackgroundTasks
2. Implicitly via dependency injection using Depends to activate a function
   that performs a task in the background
"""
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks, Depends, FastAPI

app = FastAPI()
HERE = Path(__file__).parent
LOGFILE = HERE.joinpath('log.txt')


def write_log(message: str):
    print(f'Writing {message} to file {str(LOGFILE)}')
    with LOGFILE.open('a') as log:
        log.write(message)
    print('Finished writing to logfile')


def get_query(background_tasks: BackgroundTasks, q: Optional[str] = None):
    print(f'Got q={q}')
    if q:
        message = f"found query: {q}\n"
        background_tasks.add_task(write_log, message)
    return q


@app.post("/send-notification/{email}")
async def send_notification(
    email: str, background_tasks: BackgroundTasks, q: str = Depends(get_query)
):
    message = f'Message to {email} q={q}\n'
    background_tasks.add_task(write_log, message)
    return {"message": "Message sent"}
