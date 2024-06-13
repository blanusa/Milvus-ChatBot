from typing import List
from fastapi import HTTPException
import httpx
from pydantic import BaseModel
from pymilvus import Collection


class LandmarkInsert(BaseModel):
    landmark :List[str]
    city : List[str]
    region : List[str]
    numberofcitizens : List[int]

class LandmarkSearch(BaseModel):
    landmark : List[str]

class LandmarkDelete(BaseModel):
    identifikator : List[int]

class LandmarkUpsert(BaseModel):
    identifikator : List[int]
    landmark :List[str]
    city : List[str]
    region : List[str]
    numberofcitizens : List[int]

async def InsertToLandmarks(body,nlp):
    try:
        test_collection = "LandmarkCollection"
        collection = Collection(name=test_collection)
        data = [
            body.landmark,
            body.city,
            body.region,
            body.numberofcitizens,
            [nlp(lmr).vector for lmr in body.landmark]
        ]
        mr = collection.insert(data)
        print(f"Insert result: {mr}")
        collection.flush()
        return mr
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}
    
async def SearchLandmarkText(body,nlp,client):

    try:
        vectors = [nlp(name).vector for name in body.landmark]

        res = client.search(
            collection_name="LandmarkCollection",
            data=vectors,
            limit=5,
            search_params={"metric_type": "L2", "params": {}}
        )

        search_result_ids = [j["id"] for i in res for j in i]
        
        if not search_result_ids:
            raise HTTPException(status_code=404, detail="No search results found")

        entities = client.get(
            collection_name="LandmarkCollection",
            ids=search_result_ids
        )
        returnValues = []
        for entity in entities : 
            print(entity["id"])
            print(entity["Landmark"]) 
            returnValues.append([entity["id"],entity["Landmark"]])
        return returnValues
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}
    
async def DeleteLandmarkEntity(body):
    try:
        collection_name="LandmarkCollection"
        collection = Collection(collection_name)
        collection.delete(f"id in {body.identifikator}")
        return {"message" : "Deleted entities."}
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}
    
async def UpsertLandmarkEntity(body,nlp):
    try:
        collection_name="LandmarkCollection"
        collection = Collection(collection_name)
        collection.delete(f"id in {body.identifikator}")
        data = [
            body.landmark,
            body.city,
            body.region,
            body.numberofcitizens,
            [nlp(lmr).vector for lmr in body.landmark]
        ]
        mr = collection.insert(data)
        print(f"Insert result: {mr}")
        collection.flush()
        return {"message":"Update completed."}
   
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}

async def TransactionLandmarkUpsert(body,nlp):
    try:

        headers = {
        "Content-Type": "application/json",
        }
        payload = {
        "text": body.landmark[0],
        "vectordatabaseid": body.identifikator
        }
        async with httpx.AsyncClient() as client:
            response = await client.post("http://host.docker.internal:8081/Text/insert", headers=headers, json=payload)
        if response:        
            try:
                collection_name="LandmarkCollection"
                collection = Collection(collection_name)
                collection.delete(f"id in {body.identifikator}")
                data = [
                    body.landmark,
                    body.city,
                    body.region,
                    body.numberofcitizens,
                    [nlp(lmr).vector for lmr in body.landmark]
                ]
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
 