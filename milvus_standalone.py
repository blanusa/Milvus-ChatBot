from pymilvus import connections, utility, MilvusException, MilvusClient, Collection
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import spacy
import json

app = FastAPI()

MILVUS_HOST = 'standalone'
MILVUS_PORT = 19530
nlp = spacy.load("en_core_web_lg")
connections.connect(host="standalone", port="19530")
client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}", token="root:Milvus")


#collection_bus_routes = Collection(name="BusRoutes")


index_params = {
    "index_type": "IVF_FLAT",
    "metric_type": "L2",
    "params": {
        "nlist": 100
    }
}

#collection_bus_routes.create_index(
# field_name="Vector",
#  index_params=index_params,
#  index_name="busroutes_index"
#)

#collection_bus_routes.load()

@app.get("/collections/getvector1/{vector_id}")
async def get_vector(
    vector_id: int
):
    try:
        client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}", token="root:Milvus")

        vector_data = client.get(collection_name="collection_test", ids=[vector_id])

        if vector_data:
            vector_dict = {
                "id": vector_id,
                "test_field": vector_data[0]["description"],
            }
            return JSONResponse(content={"vector_data": vector_dict})
        else:
            return JSONResponse(content={"message": "Vector not found"}, status_code=404)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/")
async def func():
    try:
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
       # count = collection.num_entities
        return {"message": "Count of entities in collection", "count": 123123}
    except Exception as e:
        return {"message": "Error occurred while getting entity count:", "error": str(e)}

@app.get("/test-milvus-connection/")
async def test_milvus_connection():
    try:

        client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}", token="root:Milvus")
        status = client.get_collection_stats(collection_name="test_name")
        return {"message": "Connected to Milvus", "status": status}
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}

class Insert(BaseModel):
    name :List[str]

class Search(BaseModel):
    name: List[str]

class Update(BaseModel):
    identifikator : List[int]
    name : List[str]

class Delete(BaseModel):
    identifikator : List[int]

@app.post("/insertText")
async def insertText(body : Insert):
    try:
        test_collection = "text_collection"
        collection = Collection(name=test_collection)
        embedding = [nlp(name).vector for name in body.name]
        name = body.name
       #ids = text.ids
        #data = [ids,embedding,name]
        data = [embedding,name]
        mr = collection.insert(data)
        print(f"Insert result: {mr}")
        collection.flush()
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}
    
@app.post("/searchText")
async def searchText(body: Search):
    try:
        vectors = [nlp(name).vector for name in body.name]

        res = client.search(
            collection_name="text_collection",
            data=vectors,
            limit=5,
            search_params={"metric_type": "L2", "params": {}}
        )

        search_result_ids = [j["id"] for i in res for j in i]
        
        if not search_result_ids:
            raise HTTPException(status_code=404, detail="No search results found")

        entities = client.get(
            collection_name="text_collection",
            ids=search_result_ids
        )
        returnValues = []
        for entity in entities : 
            print(entity["ID"])
            print(entity["name"]) 
            returnValues.append([entity["ID"],entity["name"]])
        return returnValues
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}
    
@app.post("/upsertText")
async def upsertText(body : Update):
    try:

        headers = {
        "Content-Type": "application/json",
        }
        payload = {
        "text": body.name[0],
        "vectordatabaseid": body.identifikator
        }
        async with httpx.AsyncClient() as client:
            response = await client.post("http://host.docker.internal:8081/Text/insert", headers=headers, json=payload)
        if response:        
            try:
                collection_name="text_collection"
                collection = Collection(collection_name)
                collection.delete(f"ID in {body.identifikator}")
                embedding = [nlp(name).vector for name in body.name]
                name = body.name
                data = [embedding,name]
                mr = collection.insert(data)

                print(f"Insert result: {mr}")
                collection.flush()
                return {"message":"Update completed."}
            except Exception as e:
                await client.post("http://host.docker.internal:8081/Text/delete", headers=headers, json=payload)
                return {"message": "Transaction cancelled: \n Error occurred during Milvus connection:", "error": str(e)}
        else: 
            return {"message" : "Transaction failed"}
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}
    
@app.post("/deleteText")
async def deleteText(body : Delete):
    try:
        collection_name="text_collection"
        collection = Collection(collection_name)
        collection.delete(f"ID in {body.identifikator}")
        return {"message" : "Deleted entities."}
    
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}
        
      

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
#docker run --name attu -p 8000:3000 -e HOST_URL=http://192.168.1.84:8000 -e MILVUS_URL=http://192.168.1.84:19530 zilliz/attu:v2.3.6 ATTU GUI ZA MILVUS
