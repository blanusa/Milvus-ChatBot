from pymilvus import connections, utility, MilvusException
from fastapi import FastAPI
import httpx

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

@app.get("/springBoot")
async def func():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://host.docker.internal:9099/hi")
        return response.json()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
#docker run --name attu -p 8000:3000 -e HOST_URL=http://192.168.1.84:8000 -e MILVUS_URL=http://192.168.1.84:19530 zilliz/attu:v2.3.6 ATTU GUI ZA MILVUS
