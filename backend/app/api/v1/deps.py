from typing import Annotated

from fastapi import Query

SeasonParam = Annotated[int | None, Query(description="Season year; defaults to the latest ingested season")]
