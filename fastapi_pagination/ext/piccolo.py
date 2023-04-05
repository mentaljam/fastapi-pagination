__all__ = ["paginate"]

from copy import deepcopy
from typing import Optional, Type, Union, TypeVar, Any

from piccolo.query import Select
from piccolo.query.methods.select import Count
from piccolo.table import Table

from .utils import generic_query_apply_params
from ..api import create_page, apply_items_transformer
from ..bases import AbstractParams
from ..types import AdditionalData, SyncItemsTransformer
from ..utils import verify_params

T = TypeVar("T", bound=Table, covariant=True)


async def paginate(
    query: Union[Select[T], Type[T]],
    params: Optional[AbstractParams] = None,
    *,
    transformer: Optional[SyncItemsTransformer] = None,
    additional_data: AdditionalData = None,
) -> Any:
    params, raw_params = verify_params(params, "limit-offset")

    if not isinstance(query, Select):
        query = query.select()

    # query object is mutable, so we need deepcopy of it
    query = deepcopy(query)

    # need another copy for count query
    count_query = deepcopy(query)
    count_query.columns_delegate.selected_columns = []

    total = 0
    if row := await count_query.columns(Count()).first():
        total = row["count"]

    items = await generic_query_apply_params(query, raw_params)
    t_items = await apply_items_transformer(items, transformer, async_=True)

    return create_page(
        t_items,
        total,
        params,
        **(additional_data or {}),
    )
