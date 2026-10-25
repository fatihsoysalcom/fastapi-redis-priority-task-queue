# fastapi-redis-priority-task-queue
This example demonstrates a priority task scheduler using FastAPI as the web API and Redis as the priority queue. Tasks can be added with varying priority levels, and a simulated worker processes them from Redis, always picking the highest priority task first. While the original article mentions C++ for high-performance workers, this example uses P
