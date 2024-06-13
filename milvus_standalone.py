from pymilvus import connections, utility, MilvusException, MilvusClient, Collection
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import spacy

from controllers.BusRoutesCollectionController import BusRouteDelete, BusRouteInsert, BusRouteSearch, BusRouteUpsert, DeleteBusRoute, InsertToBusRoutes, SearchBusRoutes, UpsertBusRoute
from controllers.BusStopsCollectionController import BusStopDelete, BusStopInsert, BusStopSearch, BusStopUpsert, DeleteBusStopEntity, InsertToBusStops, SearchBusStopText, UpsertBusStopEntity
from controllers.DTO import DeleteText, GetEntityCount, Insert, Querry, SearchText, TestMilvusCollection, Update, Search, Delete, UpsertText, getAllCollection, insertInTextCollection
from controllers.LandmarkCollectionController import DeleteLandmarkEntity, InsertToLandmarks, LandmarkDelete, LandmarkInsert, LandmarkSearch, LandmarkUpsert, SearchLandmarkText, TransactionLandmarkUpsert, UpsertLandmarkEntity
from insertScripts.busRoutes import insertBusRoutes
from insertScripts.busStops import insertBusStops
from insertScripts.landmarks import insertLandmarks

app = FastAPI()

MILVUS_HOST = 'standalone'
MILVUS_PORT = 19530
nlp = spacy.load("en_core_web_lg")
connections.connect(host="standalone", port="19530")
client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}", token="root:Milvus")

insertLandmarks(nlp)
insertBusStops(nlp)
insertBusRoutes(nlp)


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

# <<<<<<=============================================Text collection (obrisana)=============================================>>>>>>
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

# <<<<<<=============================================INSERTS=============================================>>>>>>
@app.post("/insertToLandmarks")
async def insertToLandmarks(body : LandmarkInsert):
    await InsertToLandmarks(body,nlp)

@app.post("/insertToBusRoutes")
async def insertToBusRoutes(body : BusRouteInsert):
    res = await InsertToBusRoutes(body,nlp)
    return res

@app.post("/insertToBusStops")
async def insertToBusStops(body : BusStopInsert):
    res = await InsertToBusStops(body,nlp)
    return res


# <<<<<<=============================================Vector search=============================================>>>>>>
@app.post("/searchLandmarkCollection")
async def searchLandmarkText(body : LandmarkSearch):
    res = await SearchLandmarkText(body,nlp,client)
    print(res)
    return res

@app.post("/searchBusRouteCollection")
async def searchBusRoutes(body : BusRouteSearch):
    res = await SearchBusRoutes(body,nlp,client)
    print(res)
    return res

@app.post("/searchBusStopCollection")
async def searchBusStops(body: BusStopSearch):
    res = await SearchBusStopText(body,nlp,client)
    print(res)
    return res

# <<<<<<=============================================DELETES=============================================>>>>>>
@app.post("/deleteFromLandmarks")
async def deleteLandmarkEntity(body : LandmarkDelete):
    res = await DeleteLandmarkEntity(body)
    print(res)
    return res

@app.post("/deleteFromBusRoutes")
async def deleteBusRoute(body : BusRouteDelete):
    res = await DeleteBusRoute(body)
    print(res)
    return res

@app.post("/deleteFromBusStops")
async def deleteBusStop(body : BusStopDelete):
    res = await DeleteBusStopEntity(body)
    print(res)
    return res

# <<<<<<=============================================Upserts=============================================>>>>>>
@app.post("/upsertLandmarkEntity")
async def deleteLandmarkEntity(body : LandmarkUpsert):
    res = await UpsertLandmarkEntity(body,nlp)
    print(res)
    return res

@app.post("/transactionalLandmarksUpsert")
async def transaction(body : LandmarkUpsert):
    res = await TransactionLandmarkUpsert(body,nlp)
    print(res)
    return res

@app.post("/upsertBusRoute")
async def upsertBusRoute(body : BusRouteUpsert):
    res = await UpsertBusRoute(body,nlp)
    print(res)
    return res

@app.post("/upsertBusStop")
async def upsertBusStop(body : BusStopUpsert):
    res = await UpsertBusStopEntity(body,nlp)
    print(res)
    return res

# <<<<<<=============================================Querry=============================================>>>>>>
@app.post("/pitamSePitam")
async def searchCollections(body: Querry):
    try:
        collection_name=body.collection[0]
        collection = Collection(collection_name)
        res = collection.query(
            expr = body.querry[0],
            offset = body.offset,
            limit = body.numberofresults, 
            output_fields = body.outputFields,
        )
        print(res)
        return res
    except Exception as e:
        return {"message" : "Error occurred during Milvus connection:", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
#docker run --name attu -p 8000:3000 -e HOST_URL=http://192.168.1.5:8000 -e MILVUS_URL=http://192.168.1.5:19530 zilliz/attu:v2.3.6
