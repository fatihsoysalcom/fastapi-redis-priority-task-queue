import uuid
import json
import time
import asyncio
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis

# --- Configuration ---
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_KEY_PRIORITY_QUEUE = "priority_tasks"

# --- Redis Client Initialization ---
try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    r.ping() # Test connection
    print(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
except redis.exceptions.ConnectionError as e:
    print(f"Could not connect to Redis: {e}. Please ensure Redis is running.")
    r = None # Set to None to indicate no connection

# --- Pydantic Models ---
class TaskCreate(BaseModel):
    data: str
    priority: int = 5 # Default priority if not provided

class Task(BaseModel):
    id: str
    data: str
    priority: int
    created_at: float

# --- FastAPI Application ---
app = FastAPI(
    title="Priority Task Scheduler",
    description="A simple FastAPI application demonstrating a priority task scheduler using Redis."
)

@app.post("/tasks", response_model=Task)
async def add_task(task_create: TaskCreate):
    """
    Adds a new task to the priority queue in Redis.
    Higher 'priority' values mean higher priority (processed first).
    """
    if not r:
        raise HTTPException(status_code=500, detail="Redis connection not available.")

    task_id = str(uuid.uuid4())
    current_time = time.time()
    
    task_data = Task(
        id=task_id,
        data=task_create.data,
        priority=task_create.priority,
        created_at=current_time
    )
    
    score = float(task_create.priority)
    
    # Add the task to the sorted set. The score determines its position.
    # Higher score = higher priority.
    r.zadd(REDIS_KEY_PRIORITY_QUEUE, {task_data.json(): score}) # Concept: Task added to Redis priority queue
    
    print(f"Task '{task_id}' added with priority {task_create.priority}")
    return task_data

@app.get("/tasks/process", response_model=Optional[Task])
async def process_next_task():
    """
    Processes the highest priority task from the queue.
    This simulates a worker picking up a task.
    """
    if not r:
        raise HTTPException(status_code=500, detail="Redis connection not available.")

    # Fetch the highest priority task (highest score) from the sorted set.
    # ZREVRANGE returns elements in descending order of score.
    # We get the first element (index 0 to 0).
    tasks_in_queue = r.zrevrange(REDIS_KEY_PRIORITY_QUEUE, 0, 0)
    
    if not tasks_in_queue:
        print("No tasks in the queue to process.")
        return None
    
    task_json = tasks_in_queue[0]
    
    # Atomically remove the task from the queue.
    # This is crucial in a multi-worker scenario to prevent multiple workers
    # from processing the same task.
    removed_count = r.zrem(REDIS_KEY_PRIORITY_QUEUE, task_json) # Concept: Task removed from Redis
    
    if removed_count == 0:
        print(f"Task '{task_json}' was already processed by another worker.")
        return None
        
    processed_task = Task.parse_raw(task_json)
    
    # Simulate work being done
    print(f"Processing task '{processed_task.id}' with data: '{processed_task.data}' (Priority: {processed_task.priority})...")
    await asyncio.sleep(1) # Simulate some async work
    print(f"Task '{processed_task.id}' completed.") # Concept: Task processed by worker
    
    return processed_task

# To run this file directly with `python main.py` for development/testing:
# This is not the standard way to run FastAPI with Uvicorn in production,
# but it makes the file self-contained for a quick demo.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
