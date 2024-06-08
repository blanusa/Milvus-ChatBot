from pymilvus import connections, utility, MilvusException
from fastapi import FastAPI

app = FastAPI()

connections.connect(host="standalone", port="19530")

@app.get("/")
async def func():
    try:
        # List all collections
        collections = utility.list_collections()
        print(f"List all collections:\n", collections)
    except MilvusException as e:
        print(e)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)