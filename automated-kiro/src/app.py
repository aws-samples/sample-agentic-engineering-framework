from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/users")
def users():
    return {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
