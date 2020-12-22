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
from logging import getLogger
from fastapi import BackgroundTasks, FastAPI
from .service_util import *

app = FastAPI()

logger = getLogger(__name__)

# Initialize with 'booting' before we're done loading stuff
STATUS = ServiceStatus(service_type='signed worker',
                       status='booting')


@app.get('/health')
async def health():
    """Health endpoint"""
    return {'status': STATUS.status}


@app.get('/status', response_model=ServiceStatus)
async def status():
    """Gives the current status of this service"""
    return STATUS


@app.post('/query')
async def query(search_query: NetworkSearchQuery,
                bgt: BackgroundTasks):
    # todo handle query and send to background, return 202 if everything
    #  went OK
    pass


# Change to 'online' after everything is loaded
STATUS.status = 'online'
