# FastAPI Redis Priority Task Queue

This example demonstrates a priority task scheduler using FastAPI as the web API and Redis as the priority queue. Tasks can be added with varying priority levels, and a simulated worker processes them from Redis, always picking the highest priority task first. While the original article mentions C++ for high-performance workers, this example uses Python for simplicity to illustrate the core scheduling logic.

## Language

`python`

## How to Run

1. Ensure Redis is running (e.g., `docker run --name my-redis -p 6379:6379 -d redis`).
2. Install Python dependencies: `pip install fastapi uvicorn redis pydantic`.
3. Run the application: `uvicorn main:app --reload`.
4. Open your browser or use `curl` to interact:
   - Add a low priority task: `curl -X POST -H "Content-Type: application/json" -d '{"data":"low priority task", "priority":1}' http://127.0.0.1:8000/tasks`
   - Add a high priority task: `curl -X POST -H "Content-Type: application/json" -d '{"data":"high priority task", "priority":10}' http://127.0.0.1:8000/tasks`
   - Process the next highest priority task: `curl http://127.0.0.1:8000/tasks/process`

## Original Article

This example accompanies the Turkish article: [FastAPI, Redis ve C++ ile Öncelikli Görev Zamanlayıcı Nasıl Oluşturulur?](https://fatihsoysal.com/blog/fastapi-redis-ve-c-ile-oncelikli-gorev-zamanlayici-nasil-olusturulur/).

## License

MIT — see [LICENSE](LICENSE).
