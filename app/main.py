from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from app.db import database, User

app = FastAPI(title="FastAPI, Docker, and Traefik")

# Prometheus metrics
nb_of_requests_counter = Counter(
    'nb_of_requests',
    'Number of successful requests made to the app',
    ['method', 'endpoint']
)

exceptions_counter = Counter(
    'exceptions_total',
    'Total number of exceptions raised in the application',
    []
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        endpoint = request.url.path
        method = request.method
        try:
            response = await call_next(request)
            nb_of_requests_counter.labels(
                method=method, endpoint=endpoint).inc()
            return response
        except Exception as e:
            exceptions_counter.inc()
            raise e from None


# Add the middleware to the app
app.add_middleware(MetricsMiddleware)


@app.get("/")
async def read_root():
    return await User.objects.all()


@app.on_event("startup")
async def startup():
    if not database.is_connected:
        await database.connect()
    # create a dummy entry
    await User.objects.get_or_create(email="test@test.com")
    await User.objects.get_or_create(email="coucou@antoine.com")



@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()


@app.get("/metrics")
async def get_metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

#comment
