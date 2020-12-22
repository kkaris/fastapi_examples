"""
This file contains helper functions and basemodels for the services
"""
import json
import logging
from typing import Optional, Dict, List
from pathlib import Path
from pydantic import BaseModel
from indra_depmap_service.util import get_query_hash, dump_json_to_s3


logger = logging.getLogger(__name__)


__all__ = ['NetworkSearchQuery', 'Job', 'JobStatus', 'ServiceStatus',
           'Edge', 'PathResult', 'QueryResult', 'upload_json']

HERE = Path(__file__).parent
DATA_DIR = HERE.parent.absolute().joinpath('data')


class ServiceStatus(BaseModel):
    """Service status model"""
    service_type: str  # Specify unsigned worker, signed worker, master etc
    status: str  # Specify available or loading or similar


class NetworkSearchQuery(BaseModel):
    """Small version of final NetworkSearchQuery"""
    source: str
    target: Optional[str]
    signed: Optional[int] = None

    def get_hash(self):
        """Get the corresponding query hash of the query"""
        return get_query_hash(self.dict())


class Job(BaseModel):
    """Defines a job"""
    status: str
    id: str
    query: NetworkSearchQuery


class JobStatus(BaseModel):
    """Jobstatus model providing META data"""
    status: str
    id: str
    fname: Optional[str] = None
    location: Optional[str] = None  # e.g. URL or s3 path


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


# HELPER FUNCTIONS
def upload_json(model: BaseModel, name: str):
    """Dumps json to s3 for public read access"""
    # Todo make async with aioboto3
    # logger.info('Writing file')
    # dump_json_to_s3(name, model.dict(), public=True)
    with DATA_DIR.joinpath(name).open('w') as f:
        logger.info(f'Writing to file {DATA_DIR.joinpath(name)}')
        json.dump(fp=f, obj=model.dict())
