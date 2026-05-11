from fastapi import FastAPI

app = FastAPI(title="Field Sample Management API")

# Routers and business logic will be added here later.

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Field Sample Management API scaffold"}
