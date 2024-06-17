from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/hi")
async def func():
    return {"message" : "Hello from fastapi2"}