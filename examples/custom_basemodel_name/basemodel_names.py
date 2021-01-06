"""
This example shows how to add attributes to basemodels where the attribute
name itself is dynamic

Following this github issue on pydantic
https://github.com/samuelcolvin/pydantic/issues/1802

ToDo: mix-and-match regular model attributes and custom attribute names
"""

from pydantic import BaseModel
from typing import Dict


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


class MyModel(BaseModel):
    """Model holding StmtInfo with the attribute name being variable"""
    subj: str
    obj: str


class MyModel_(BaseModel):
    __root__: Dict[str, StmtInfo]

    # This allows . notation to be used, sadly it won't allow for PyCharm to
    # recognize it as part of the model
    def __getattr__(self, item):
        return self.__root__[item]


if __name__ == '__main__':
    stmt_info = dict(stmt_hash='123456789', stmt_type='Activation',
                     evidence_count=5, belief=0.86,
                     source_counts={'sparser': 4, 'tas': 1},
                     english='A activates B', curated=True, weight=0.12)
    # data = {'Activation': stmt_info, 'subj': 'A', 'obj': 'B'}
    # model = MyModel_.parse_obj(data)
    stmt_info_copy = stmt_info.copy()
    stmt_info_copy['stmt_type'] = 'Phosphorylation'
    data = {'Activation': stmt_info,
            'Phosphorylation': stmt_info}
    model: MyModel_ = MyModel_.parse_obj(data)
    print(model.Activation)
