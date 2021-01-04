"""
This file contains helper functions and basemodels for the services
"""
import json
import pickle
import logging
import aiofiles
from typing import Optional, Dict, List, Union
from pydantic import BaseModel
from indra_depmap_service.util import NetworkSearchQuery
from . import DATA_DIR


logger = logging.getLogger(__name__)


__all__ = ['NetworkSearchQuery', 'Job', 'JobStatus', 'ServiceStatus',
           'Edge', 'PathResult', 'QueryResult', 'HealthStatus',
           'EMPTY_JOB_STATUS', 'upload_json', 'upload_json_async',
           'async_pickle_open']


class ServiceStatus(BaseModel):
    """Service status model"""
    service_type: str  # Specify unsigned worker, signed worker, master etc
    status: str  # Specify available or loading or similar
    graph_stats: Optional[Dict[str, int]] = None


class HealthStatus(BaseModel):
    """Health status model"""
    unsigned_service: str
    signed_service: str
    public_api: str


# class NetworkSearchQuery(BaseModel):
#     """Small version of final NetworkSearchQuery"""
#     source: str
#     target: Optional[str]
#     signed: Optional[str] = None
#
#     def get_hash(self):
#         """Get the corresponding query hash of the query"""
#         return get_query_hash(self.dict())


class JobStatus(BaseModel):
    """Job status model providing META data"""
    status: str
    id: str
    fname: Optional[str] = None
    location: Optional[str] = None  # e.g. URL or s3 path
    result_location: Optional[str] = None  # e.g. URL or s3 path
    error: Optional[str] = None  # In case something went wrong


EMPTY_JOB_STATUS = JobStatus(status='NA', id='NA')


class Job(BaseModel):
    """Defines a job"""
    id: str
    status: str
    query: NetworkSearchQuery
    job_status: JobStatus


# RESULT MODELS
class StmtInfo(BaseModel):
    """The stmt info for an edge"""
    stmt_hash: str
    stmt_type: str
    evidence_count: int
    belief: float
    source_counts: Dict[str, int]
    english: str
    curated: bool
    weight: float


class Edge(BaseModel):
    """The basic edge info

    Todo: restructure the statement info keys to not be the name of the
     statement type
    """
    subj: str
    obj: str
    weight_to_show: str = 'N/A'
    Complex: Optional[List[StmtInfo]] = None
    Activation: Optional[List[StmtInfo]] = None
    Inhibition: Optional[List[StmtInfo]] = None
    Acetylation: Optional[List[StmtInfo]] = None
    Methylation: Optional[List[StmtInfo]] = None
    Sumoylation: Optional[List[StmtInfo]] = None
    Ribosylation: Optional[List[StmtInfo]] = None
    Deacetylation: Optional[List[StmtInfo]] = None
    Farnesylation: Optional[List[StmtInfo]] = None
    Glycosylation: Optional[List[StmtInfo]] = None
    Hydroxylation: Optional[List[StmtInfo]] = None
    Demethylation: Optional[List[StmtInfo]] = None
    Desumoylation: Optional[List[StmtInfo]] = None
    DecreaseAmount: Optional[List[StmtInfo]] = None
    Deribosylation: Optional[List[StmtInfo]] = None
    IncreaseAmount: Optional[List[StmtInfo]] = None
    Myristoylation: Optional[List[StmtInfo]] = None
    Palmitoylation: Optional[List[StmtInfo]] = None
    Ubiquitination: Optional[List[StmtInfo]] = None
    Defarnesylation: Optional[List[StmtInfo]] = None
    Deglycosylation: Optional[List[StmtInfo]] = None
    Dehydroxylation: Optional[List[StmtInfo]] = None
    Phosphorylation: Optional[List[StmtInfo]] = None
    Demyristoylation: Optional[List[StmtInfo]] = None
    Depalmitoylation: Optional[List[StmtInfo]] = None
    Deubiquitination: Optional[List[StmtInfo]] = None
    Dephosphorylation: Optional[List[StmtInfo]] = None
    Geranylgeranylation: Optional[List[StmtInfo]] = None
    Degeranylgeranylation: Optional[List[StmtInfo]] = None


class PathResult(BaseModel):
    """Results for directed paths

    len(stmts) == len(path)-1
    """
    stmts: Optional[List[Edge]] = None
    path: Optional[List[str]] = None
    weight_to_show: List[str]
    cost: str  # string-ified float
    sort_key: str  # string-ified float


class KShortest(BaseModel):
    """Result for k-shortest paths keyed by path length
    Todo add method for filling out path_hashes??
    """
    forward: Optional[Dict[str, List[PathResult]]] = None
    backward: Optional[Dict[str, List[PathResult]]] = None
    path_hashes: List[str]


class SearchResults(BaseModel):
    """Search results"""
    paths_by_node_count: KShortest
    common_targets: List
    shared_regulators: Optional[List] = None
    common_parents: List
    timeout: bool = False
    node_not_found: Optional[str] = None


class QueryResult(BaseModel):
    """The main result model

    This model contains the search results and also meta data
    All parameters are optional to account for empty results
    """
    query_hash: str
    path_hashes: Optional[List[str]] = None
    result: Optional[SearchResults] = None
    fname: Optional[str] = None


# HELPER FUNCTIONS
def upload_json(json_dict: Union[QueryResult, JobStatus]):
    """Dumps json to s3 for public read access"""
    # logger.info('Writing file')
    # dump_json_to_s3(name, model.dict(), public=True)
    with DATA_DIR.joinpath(json_dict.fname).open('w') as f:
        logger.info(f'Writing to file {DATA_DIR.joinpath(json_dict.fname)}')
        json.dump(fp=f, obj=json_dict.dict())


async def upload_json_async(json_dict: Union[QueryResult, JobStatus]):
    """Dumps json to s3 for public read access"""
    # Todo make async with aioboto3
    # logger.info('Writing file')
    # dump_json_to_s3(name, model.dict(), public=True)
    async with aiofiles.open(DATA_DIR.joinpath(json_dict.fname), 'w') as f:
        logger.info(f'Writing to file async '
                    f'{DATA_DIR.joinpath(json_dict.fname)}')
        await f.write(json.dumps(json_dict.dict()))


async def async_pickle_open(fname: str):
    """async pickle load"""
    logger.info(f'Loading pickle file {fname} async')
    async with aiofiles.open(fname, 'rb') as f:
        obj = pickle.load(f)
    logger.info('Finished loading pickle file async')
    return obj
