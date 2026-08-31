class OpenF1Error(Exception):
    """Base class for all OpenF1 integration errors."""


class OpenF1RequestError(OpenF1Error):
    """Raised when a request to OpenF1 fails after all retries are exhausted."""


class OpenF1ValidationError(OpenF1Error):
    """Raised when an OpenF1 response doesn't match the expected schema."""
