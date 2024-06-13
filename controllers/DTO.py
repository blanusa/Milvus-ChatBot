from fastapi import HTTPException
import httpx
from pydantic import BaseModel
from typing import List

from pymilvus import Collection, MilvusClient, MilvusException, utility

import spacy

class Insert(BaseModel):
    name :List[str]

class Search(BaseModel):
    name: List[str]

class Update(BaseModel):
    identifikator : List[int]
    name : List[str]

class Delete(BaseModel):
    identifikator : List[int]

class Querry(BaseModel):
    collection : List[str]
    querry : List[str]
    outputFields : List[str]
    numberofresults : int
    offset : int

class SearchLandmarks(BaseModel):
    landmark: List[str]
    region: str
    min_citizens: int
    max_citizens: int

class SearchStops1(BaseModel):
    special_features: List[str]
    latitude: int
    longitude: int
    facilities : str

class SearchStops2(BaseModel):
    special_features: List[str]
    nearby_landmarks : str
    bus_lines : str

class SearchStops3(BaseModel):
    special_features: List[str]
    nearby_landmarks : str
    facilities : str


class SearchRoutes1(BaseModel):
    routeDescription: List[str]
    street: str
    busLine: str

class SearchRoutes2(BaseModel):
    routeDescription: List[str]
    RouteDuration: int
    DepartureTime: str

class SearchRoutes3(BaseModel):
    routeDescription: List[str]
    departureTime: str
    busLine: str

async def getAllCollection():
    try:
        collections = utility.list_collections()
        print(f"List all collections:\n", collections)
    except MilvusException as e:
        print(e)

async def insertInTextCollection(body,nlp):
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
    
async def GetEntityCount(BusStopsCollection,BusDepartCollection,LandmarkCollection):
    try:
        count1 = BusStopsCollection.num_entities
        count2 = BusDepartCollection.num_entities
        count3 = LandmarkCollection.num_entities
        return {"message": "Count of entities in collections : " + count1 +" "+ count2 +" "+ count3, "count":count1+count2+count3}
    except Exception as e:
        return {"message": "Error occurred while getting entity count:", "error": str(e)}

async def TestMilvusCollection(MILVUS_HOST,MILVUS_PORT):
    try:
        client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}", token="root:Milvus")
        status = client.get_collection_stats(collection_name="test_name")
        return {"message": "Connected to Milvus", "status": status}
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}

async def SearchText(body,nlp,client):
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
    
async def UpsertText(body,nlp):
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
    
async def DeleteText(body):
    try:
        collection_name="text_collection"
        collection = Collection(collection_name)
        collection.delete(f"ID in {body.identifikator}")
        return {"message" : "Deleted entities."}
    
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}