"""
This file contains helper functions and basemodels for the services
"""
import json
import logging
import aiofiles
from typing import Optional, Dict, List, Union
from pathlib import Path
from pydantic import BaseModel
from indra_depmap_service.util import get_query_hash, dump_json_to_s3


logger = logging.getLogger(__name__)


__all__ = ['NetworkSearchQuery', 'Job', 'JobStatus', 'ServiceStatus',
           'Edge', 'PathResult', 'QueryResult', 'HealthStatus', 'upload_json',
           'upload_json_async']

HERE = Path(__file__).parent
DATA_DIR = HERE.parent.absolute().joinpath('data')


class ServiceStatus(BaseModel):
    """Service status model"""
    service_type: str  # Specify unsigned worker, signed worker, master etc
    status: str  # Specify available or loading or similar


class HealthStatus(BaseModel):
    """Health status model"""
    unsigned_service: str
    signed_service: str
    public_api: str


class NetworkSearchQuery(BaseModel):
    """Small version of final NetworkSearchQuery"""
    source: str
    target: Optional[str]
    signed: Optional[int] = None

    def get_hash(self):
        """Get the corresponding query hash of the query"""
        return get_query_hash(self.dict())


class JobStatus(BaseModel):
    """Job status model providing META data"""
    status: str
    id: str
    fname: Optional[str] = None
    location: Optional[str] = None  # e.g. URL or s3 path
    result_location: Optional[str] = None  # e.g. URL or s3 path
    error: Optional[str] = None  # In case something went wrong


class Job(BaseModel):
    """Defines a job"""
    id: str
    status: str
    query: NetworkSearchQuery
    job_status: JobStatus


# RESULT MODELS
class Edge(BaseModel):
    """The smallest unit of result"""
    hashes: List[int]
    sources: List[Dict[str, int]]


class PathResult(BaseModel):
    """Results for directed paths"""
    one_edge: Optional[List[Edge]] = None
    two_edge: Optional[List[Edge, Edge]] = None


class QueryResult(BaseModel):
    """The main result model

    All parameters are optional to account for empty
    """
    forward_paths: Optional[PathResult] = None
    backward_paths: Optional[PathResult] = None
    shared_targets: Optional[List[Edge]] = None
    fname: Optional[str] = None


# HELPER FUNCTIONS
def upload_json(json_dict: Union[QueryResult, JobStatus]):
    """Dumps json to s3 for public read access"""
    # logger.info('Writing file')
    # dump_json_to_s3(name, model.dict(), public=True)
    with DATA_DIR.joinpath(json_dict.fname).open('w') as f:
        logger.info(f'Writing to file {DATA_DIR.joinpath(json_dict.fname)}')
        json.dump(fp=f, obj=json_dict.json())


async def upload_json_async(json_dict: Union[QueryResult, JobStatus]):
    """Dumps json to s3 for public read access"""
    # Todo make async with aioboto3
    # logger.info('Writing file')
    # dump_json_to_s3(name, model.dict(), public=True)
    async with aiofiles.open(DATA_DIR.joinpath(json_dict.fname), 'w') as f:
        logger.info(f'Writing to file async '
                    f'{DATA_DIR.joinpath(json_dict.fname)}')
        await f.write(json.dumps(json_dict.json()))
