from pymilvus import connections, utility, MilvusException, MilvusClient, Collection
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import spacy

from controllers.DTO import DeleteText, GetEntityCount, Insert, SearchText, TestMilvusCollection, Update, Search, Delete, UpsertText, getAllCollection, insertInTextCollection
from controllers.LandmarkCollectionController import DeleteLandmarkEntity, InsertToLandmarks, LandmarkDelete, LandmarkInsert, LandmarkSearch, LandmarkUpsert, SearchLandmarkText, UpsertLandmarkEntity

app = FastAPI()

MILVUS_HOST = 'standalone'
MILVUS_PORT = 19530
nlp = spacy.load("en_core_web_lg")
connections.connect(host="standalone", port="19530")
client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}", token="root:Milvus")

BusStopsCollection = Collection(name="BusStopsCollection")
BusDepartCollection = Collection(name="BusDepartCollection")
LandmarkCollection = Collection(name="LandmarkCollection")

@app.get("/")
async def func():
    await getAllCollection()

@app.get("/get-entity-count/")
async def get_entity_count():
    await GetEntityCount(BusStopsCollection,BusDepartCollection,LandmarkCollection)

@app.get("/test-milvus-connection/")
async def test_milvus_connection():
    await TestMilvusCollection(MILVUS_HOST,MILVUS_PORT)

@app.post("/insertText")
async def insertText(body : Insert):
    await insertInTextCollection(body,nlp)
    
@app.post("/searchText")
async def searchText(body: Search):
    await SearchText(body,nlp,client)
    
@app.post("/upsertText")
async def upsertText(body : Update):
    await UpsertText(body,nlp)
    
@app.post("/deleteText")
async def deleteText(body : Delete):
    await DeleteText(body)

@app.post("/insertToLandmarks")
async def insertToLandmarks(body : LandmarkInsert):
    await InsertToLandmarks(body,nlp)

@app.post("/searchLandmarkCollection")
async def searchLandmarkText(body : LandmarkSearch):
    res = await SearchLandmarkText(body,nlp,client)
    print(res)
    return res

@app.post("/deleteFromLandmarks")
async def deleteLandmarkEntity(body : LandmarkDelete):
    res = await DeleteLandmarkEntity(body)
    print(res)
    return res

@app.post("/upsertLandmarkEntity")
async def deleteLandmarkEntity(body : LandmarkUpsert):
    res = await UpsertLandmarkEntity(body,nlp)
    print(res)
    return res

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
#docker run --name attu -p 8000:3000 -e HOST_URL=http://192.168.1.24:8000 -e MILVUS_URL=http://192.168.1.24:19530 zilliz/attu:v2.3.6
