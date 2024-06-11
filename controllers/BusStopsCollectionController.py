from typing import List
from fastapi import HTTPException
from pydantic import BaseModel
from pymilvus import Collection


class BusStopInsert(BaseModel):
    name: List[str]
    latitude : List[float]
    longitude : List[float]
    buslines: List[str]
    facilities : List[str]
    nearbylandmarks : List[str]
    specialfeatures : List[str]

class BusStopSearch(BaseModel):
    specialfeatures : List[str]

class BusStopDelete(BaseModel):
    identifikator : List[int]

class BusStopUpsert(BaseModel):
    identifikator : List[int]
    name : List[str]
    latitude : List[float]
    longitude : List[float]
    buslines: List[str]
    facilities : List[str]
    nearbylandmarks : List[str]
    specialfeatures : List[str]

async def InsertToBusStops(body,nlp):

    try:
        test_collection = "BusStopsCollection"
        collection = Collection(name=test_collection)
        data = [
            body.name,
            body.latitude,
            body.longitude,
            body.buslines,
            body.facilities,
            body.nearbylandmarks,
            body.specialfeatures,
            [nlp(sfeature).vector for sfeature in body.specialfeatures]
        ]
        mr = collection.insert(data)
        print(f"Insert result: {mr}")
        collection.flush()
        return mr
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}
 
async def SearchBusStopText(body,nlp,client):
    try:
        vectors = [nlp(name).vector for name in body.specialfeatures]

        res = client.search(
            collection_name="BusStopsCollection",
            data=vectors,
            limit=5,
            search_params={"metric_type": "L2", "params": {}}
        )

        search_result_ids = [j["id"] for i in res for j in i]
        
        if not search_result_ids:
            raise HTTPException(status_code=404, detail="No search results found")

        entities = client.get(
            collection_name="BusStopsCollection",
            ids=search_result_ids
        )
        returnValues = []
        for entity in entities : 
            print(entity["id"])
            print(entity["name"])
            print(entity["latitude"])
            print(entity["longitude"])
            print(entity["bus_lines"])
            print(entity["facilities"])
            print(entity["nearby_landmarks"])
            print(entity["special_features"])
            returnValues.append([entity["id"],entity["name"],str(entity["latitude"]),str(entity["longitude"]),entity["bus_lines"],entity["facilities"],entity["nearby_landmarks"],entity["special_features"]])
        return returnValues
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}
   
async def DeleteBusStopEntity(body):
    try:
        collection_name="BusStopsCollection"
        collection = Collection(collection_name)
        collection.delete(f"id in {body.identifikator}")
        return {"message" : "Deleted entities."}
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}
        
async def UpsertBusStopEntity(body,nlp):
    try:
        collection_name="BusStopsCollection"
        collection = Collection(collection_name)
        collection.delete(f"id in {body.identifikator}")
        data = [
            body.name,
            body.latitude,
            body.longitude,
            body.buslines,
            body.facilities,
            body.nearbylandmarks,
            body.specialfeatures,
            [nlp(sfeature).vector for sfeature in body.specialfeatures]
        ]
        mr = collection.insert(data)
        print(f"Insert result: {mr}")
        collection.flush()
        return {"message":"Update completed."}
   
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}
