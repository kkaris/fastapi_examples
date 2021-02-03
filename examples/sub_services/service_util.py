"""
This file contains helper functions and basemodels for the services
"""
import json
import pickle
import logging
import aiofiles
from os import environ
from typing import Optional, Dict, List, Union, Tuple
from pathlib import Path
from pydantic import BaseModel
from indra_network_search.data_models import NetworkSearchQuery

__all__ = ['NetworkSearchQuery', 'Job', 'JobStatus', 'ServiceStatus',
           'Edge', 'PathResult', 'QueryResult', 'HealthStatus',
           'EMPTY_JOB_STATUS', 'StmtInfo', 'SearchResults', 'CommonParents',
           'KShortest', 'upload_json', 'upload_json_async',
           'async_pickle_open', 'FASTAPI_DATA_DIR']

logger = logging.getLogger(__name__)

# Set data directory
if environ.get('DATA_DIR'):
    FASTAPI_DATA_DIR = Path(environ['DATA_DIR']).absolute()
else:
    HERE = Path(__file__).parent.absolute()  # This dir
    FASTAPI_DATA_DIR = HERE.parent.joinpath('data')  # Directory in parent dir

if not FASTAPI_DATA_DIR.is_dir():
    logger.info(f'Data dir {FASTAPI_DATA_DIR} does not exist, creating...')
    FASTAPI_DATA_DIR.mkdir(parents=True)


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
     statement type, or do the __root__ trick
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
    weight_to_show: Optional[List[str]] = []
    cost: Optional[str] = 'nan'  # string-ified float
    sort_key: Optional[str] = 'nan'  # string-ified float


class KShortest(BaseModel):
    """Result for k-shortest paths keyed by path length
    Todo add method for filling out path_hashes??
    """
    forward: Optional[Union[Dict[str, List[PathResult]], Dict]] = {}
    backward: Optional[Union[Dict[str, List[PathResult]], Dict]] = {}
    path_hashes: Optional[Union[List[str], List]] = []


class CommonParents(BaseModel):
    """Result for common parents search"""
    source_ns: Optional[str] = None
    source_id: Optional[str] = None
    target_ns: Optional[str] = None
    target_id: Optional[str] = None
    common_parents: Optional[List[Tuple[str, str, str]]] = []


class SearchResults(BaseModel):
    """Search results"""
    paths_by_node_count: KShortest
    common_targets: Optional[
        Union[List[Dict[str, Union[float, List[List[Edge]]]]], List]
    ] = []
    shared_regulators: Optional[
        Union[List[Dict[str, Union[float, List[List[Edge]]]]], List]
    ] = []
    common_parents: Optional[Union[CommonParents, Dict]] = {}
    timeout: bool = False
    node_not_found: Union[str, bool] = False


class QueryResult(BaseModel):
    """The main result model

    This model contains the search results and also meta data
    All parameters are optional to account for empty results
    """
    query_hash: Optional[str] = None
    path_hashes: Optional[List[str]] = None
    result: Optional[SearchResults] = None
    fname: Optional[str] = None


# HELPER FUNCTIONS
def upload_json(json_dict: Union[QueryResult, JobStatus]):
    """Dumps json to s3 for public read access"""
    # logger.info('Writing file')
    # dump_json_to_s3(name, model.dict(), public=True)
    with FASTAPI_DATA_DIR.joinpath(json_dict.fname).open('w') as f:
        logger.info(f'Writing to file {FASTAPI_DATA_DIR.joinpath(json_dict.fname)}')
        json.dump(fp=f, obj=json_dict.dict())


async def upload_json_async(json_dict: Union[QueryResult, JobStatus]):
    """Dumps json to s3 for public read access"""
    # Todo make async with aioboto3
    # logger.info('Writing file')
    # dump_json_to_s3(name, model.dict(), public=True)
    async with aiofiles.open(FASTAPI_DATA_DIR.joinpath(json_dict.fname), 'w') as f:
        logger.info(f'Writing to file async '
                    f'{FASTAPI_DATA_DIR.joinpath(json_dict.fname)}')
        await f.write(json.dumps(json_dict.dict()))


async def async_pickle_open(fname: str):
    """async pickle load"""
    logger.info(f'Loading pickle file {fname} async')
    async with aiofiles.open(fname, 'rb') as f:
        obj = pickle.load(f)
    logger.info('Finished loading pickle file async')
    return obj
