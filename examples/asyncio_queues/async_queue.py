"""
This examples shows:
1. How to use queues
2. How to use asyncio queues specifically
3. How to asynchronously poll a "work in progress"

todo: Does this program handle the case of "previous query running when next
      request comes in"? This is in the context of one of the sub-services
      running the unsigned or the signed graph that gets a request from the
      "public" server.
      Just try to solve it with an asyncio.queue.Queue, should be enough for
      the initial use case, no?
      - If no job is running just immediately submit a job (this could mean
        put it in a queue alone and submit that queue)
      - If a job is running:
        - Start a new "waiter queue", where requests that are received while
          the current job is running are put
        - When the current query is done (how does it know that?), submit
          the "waiter queue" as the new queue
"""
import multiprocessing
from typing import Optional
from fastapi import FastAPI, Query
from asyncio import sleep as async_sleep
from asyncio.queues import Queue
from pydantic import BaseModel
from collections import deque
from indra_depmap_service.util import NetworkSearchQuery


logger = multiprocessing.get_logger()


class Job(BaseModel):
    """Defines a job"""
    source: str
    target: str
    weighted: bool = False
    id: str
    query: NetworkSearchQuery


class JobStatus(BaseModel):
    """Defines the status if a job"""
    id: str
    status: str
    location: Optional[str] = None


app = FastAPI()

latent_queue = deque([])
active_queue = Queue()

latent_queue.append()
latent_queue.pop()