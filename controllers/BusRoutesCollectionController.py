from typing import List
from fastapi import HTTPException
from pydantic import BaseModel
from pymilvus import Collection


class BusRouteInsert(BaseModel):
    street : List[str]
    busline : List[str]
    departureTime : List[str]
    routedescription : List[str]
    routeduration : List[int]

class BusRouteSearch(BaseModel):
    routedescription : List[str]

class BusRouteDelete(BaseModel):
    identifikator : List[int]

class BusRouteUpsert(BaseModel):
    identifikator : List[int]
    street : List[str]
    busline : List[str]
    departureTime : List[str]
    routedescription : List[str]
    routeduration : List[int]


async def InsertToBusRoutes(body,nlp):
    try:
        test_collection = "BusDepartCollection"
        collection = Collection(name=test_collection)
        data = [
            body.street,
            body.busline,
            body.departureTime,
            body.routedescription,
            body.routeduration,
            [nlp(description).vector for description in body.routedescription]
        ]
        mr = collection.insert(data)
        print(f"Insert result: {mr}")
        collection.flush()
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}
    
async def SearchBusRoutes(body,nlp,client):
    try:
        vectors = [nlp(name).vector for name in body.routedescription]

        res = client.search(
            collection_name="BusDepartCollection",
            data=vectors,
            limit=5,
            search_params={"metric_type": "L2", "params": {}}
        )

        search_result_ids = [j["id"] for i in res for j in i]
        
        if not search_result_ids:
            raise HTTPException(status_code=404, detail="No search results found")

        entities = client.get(
            collection_name="BusDepartCollection",
            ids=search_result_ids
        )
        returnValues = []
        for entity in entities : 
            print(entity["id"])
            print(entity["BusLine"]) 
            print(entity["RouteDescription"])
            print(entity["RouteDuration"])
            returnValues.append([entity["id"],entity["BusLine"],entity["RouteDescription"],entity["RouteDuration"]])
        return returnValues
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}

async def DeleteBusRoute(body):
    try:
        collection_name="BusDepartCollection"
        collection = Collection(collection_name)
        collection.delete(f"id in {body.identifikator}")
        return {"message" : "Deleted entities."}
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}
    
async def UpsertBusRoute(body,nlp):
    try:
        collection_name="BusDepartCollection"
        collection = Collection(collection_name)
        collection.delete(f"id in {body.identifikator}")
        data = [
            body.street,
            body.busline,
            body.departureTime,
            body.routedescription,
            body.routeduration,
            [nlp(description).vector for description in body.routedescription]
        ]
        mr = collection.insert(data)
        print(f"Insert result: {mr}")
        collection.flush()
        return {"message":"Update completed."}
   
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}
    