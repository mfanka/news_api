from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=60)


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class NewsCreate(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    content: str = Field(min_length=20, max_length=20000)
    author: str = Field(min_length=2, max_length=80)
    category_id: int = Field(gt=0)
    is_published: bool = True


class NewsUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=5, max_length=200)
    content: str | None = Field(default=None, min_length=20, max_length=20000)
    author: str | None = Field(default=None, min_length=2, max_length=80)
    category_id: int | None = Field(default=None, gt=0)
    is_published: bool | None = None


class NewsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    content: str
    author: str
    is_published: bool
    created_at: datetime
    updated_at: datetime
    category: CategoryOut


class NewsListOut(BaseModel):
    items: list[NewsOut]
    total: int
    page: int
    page_size: int


class CategoryStatsOut(BaseModel):
    category_id: int
    category_name: str
    news_count: int
