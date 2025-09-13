# app/tasks/queue.py
from redis import Redis
from rq import Queue

from app.core.config import settings

# Establish a connection to the Redis server using the URL from settings.
# Note: decode_responses=True is NOT used, as RQ expects bytes.
redis_conn = Redis.from_url(settings.REDIS_URL)

# Create a Redis Queue instance named 'default'.
# This 'q' object is the main entry point for enqueueing background jobs
# from anywhere in the application (e.g., from an API endpoint).
# The connection is passed explicitly, which is the recommended practice.
q = Queue("default", connection=redis_conn)