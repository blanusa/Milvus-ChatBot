from pymilvus import connections, utility, MilvusException, MilvusClient, Collection
from fastapi import FastAPI
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import spacy

MILVUS_HOST = 'standalone'
MILVUS_PORT = 19530
app = FastAPI()

nlp = spacy.load('en_core_web_lg')
connections.connect(host="standalone", port="19530")

BusStopsCollection = Collection(name="BusStopsCollection")
BusDepartCollection = Collection(name="BusDepartCollection")
LandmarkCollection = Collection(name="LandmarkCollection")

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


@app.get("/get-entity-count/")
async def get_entity_count():
    try:
        count1 = BusStopsCollection.num_entities
        count2 = BusDepartCollection.num_entities
        count3 = LandmarkCollection.num_entities
        return {"message": "Count of entities in collections : " + count1 +" "+ count2 +" "+ count3, "count":count1+count2+count3}
    except Exception as e:
        return {"message": "Error occurred while getting entity count:", "error": str(e)}


@app.get("/test-milvus-connection/")
async def test_milvus_connection():
    try:
        # Check if connected to Milvus
        client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}", token="root:Milvus")
        status = client.get_collection_stats(collection_name="test_name")
        return {"message": "Connected to Milvus", "status": status}
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}

class Item(BaseModel):
    embedding : List[float]
    name: List[str]

@app.post("/insertText")
async def insertText(text : Item):
    try:
        test_collection = "text_collection"
        collection = Collection(name=test_collection)
        embedding = text.embedding
        name = text.name
        data = [[embedding],name]
        mr = collection.insert(data)
        print(f"Insert result: {mr}")
        
        # Step 6: Flush to persist data
        collection.flush()
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
#docker run --name attu -p 8000:3000 -e HOST_URL=http://192.168.1.24:8000 -e MILVUS_URL=http://192.168.1.24:19530 zilliz/attu:v2.3.6
