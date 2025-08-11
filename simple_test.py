from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/api/test")
def test_endpoint():
    return {"status": "active", "version": "1.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)