class TwoGISAuthError(Exception):
    """Raised when 2GIS returns HTTP 403 (invalid/revoked API key or quota exceeded)."""


class TwoGISRateLimitError(Exception):
    """Raised when 2GIS returns HTTP 429 (rate limit exceeded)."""


class TwoGISServerError(Exception):
    """Raised when 2GIS returns an HTTP 5xx server error."""


class TwoGISTimeoutError(Exception):
    """Raised when an httpx request to 2GIS times out."""
