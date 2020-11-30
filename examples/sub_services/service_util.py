"""
Add:
- pydantic BaseModel for defining POST request body, see here:
  https://fastapi.tiangolo.com/tutorial/body/

"""
from typing import Optional, Union
from pydantic import BaseModel, validator


# __all__ = ['QueryBody', 'QueryBodySum', 'WriteToLogQuery']
__all__ = ['WriteToLogQuery']


# class QueryBody(BaseModel):
#     source: Optional[str]  # Todo: check if A XOR B possible
#     target: Optional[str]
#     sign: Optional[int, str]
#     max_paths: int
#
#     # See https://github.com/samuelcolvin/pydantic/issues/1223
#     @validator('source', 'target')
#     def prevent_both_none(self, s, t):
#         assert s or t, 'At least one of source or target must be provided'
#         return s, t


# class QueryBodySum(BaseModel):
#     a: float
#     b: float


class WriteToLogQuery(BaseModel):
    address: str
    message: Optional[str]
