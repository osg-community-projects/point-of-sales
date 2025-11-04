from fastapi import Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from typing import Optional

class CommonQueryParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(
            settings.default_page_size, 
            ge=1, 
            le=settings.max_page_size, 
            description="Number of records to return"
        )
    ):
        self.skip = skip
        self.limit = limit

class SearchQueryParams(CommonQueryParams):
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
        search: Optional[str] = Query(None, description="Search query")
    ):
        super().__init__(skip, limit)
        self.search = search

def get_common_params(params: CommonQueryParams = Depends()) -> CommonQueryParams:
    return params

def get_search_params(params: SearchQueryParams = Depends()) -> SearchQueryParams:
    return params
