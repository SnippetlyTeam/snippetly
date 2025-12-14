"""
Prometheus metrics middleware for FastAPI

Tracks HTTP requests, response times, and custom application metrics.
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from time import time
import logging

logger = logging.getLogger(__name__)

# HTTP Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests currently being processed',
    ['method', 'endpoint']
)

# Application Metrics
active_users = Gauge(
    'snippetly_active_users',
    'Number of active users (logged in last 24h)'
)

total_snippets = Gauge(
    'snippetly_total_snippets',
    'Total number of code snippets'
)

database_connections = Gauge(
    'snippetly_database_connections',
    'Number of active database connections',
    ['database']
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track HTTP requests with Prometheus metrics.

    Tracks:
    - Request count by method, endpoint, and status code
    - Request duration histogram
    - Requests in progress gauge
    """

    async def dispatch(self, request: Request, call_next):
        # Skip metrics endpoint itself to avoid recursion
        if request.url.path == "/api/metrics":
            return await call_next(request)

        # Extract endpoint pattern (remove IDs and dynamic parts)
        endpoint = self._get_endpoint_pattern(request)
        method = request.method

        # Track request in progress
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()

        # Start timer
        start_time = time()

        try:
            # Process request
            response = await call_next(request)

            # Record metrics
            duration = time() - start_time
            status_code = response.status_code

            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            return response

        except Exception as e:
            # Record error
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=500
            ).inc()

            logger.error(f"Request failed: {method} {endpoint} - {str(e)}")
            raise

        finally:
            # Decrement in-progress counter
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()

    def _get_endpoint_pattern(self, request: Request) -> str:
        """
        Extract endpoint pattern from request path.

        Examples:
            /api/v1/snippets/123 -> /api/v1/snippets/{id}
            /api/v1/users/abc-def -> /api/v1/users/{id}
        """
        path = request.url.path

        # Common patterns
        patterns = [
            ('/api/v1/snippets/', '/api/v1/snippets/{id}'),
            ('/api/v1/users/', '/api/v1/users/{id}'),
            ('/api/v1/auth/verify/', '/api/v1/auth/verify/{token}'),
        ]

        for prefix, pattern in patterns:
            if path.startswith(prefix) and len(path) > len(prefix):
                return pattern

        return path


def metrics_endpoint() -> Response:
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus format for scraping.
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
