from ninja import FilterSchema, Field # 必须导入 FilterSchema
from typing import Optional

class ContestFilter(FilterSchema): # 必须继承 FilterSchema
    title: Optional[str] = Field(None, q='title__icontains')
    # 如果没有 q 属性，它会默认匹配字段名
    status: Optional[int] = None