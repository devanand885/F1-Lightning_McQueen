from pydantic import BaseModel


class SearchResult(BaseModel):
    type: str  # "driver" | "constructor" | "circuit" | "meeting" | "session"
    id: int
    title: str
    subtitle: str | None
