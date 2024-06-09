from pymilvus import connections, utility, MilvusException, MilvusClient, Collection, FieldSchema, CollectionSchema, DataType
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import csv
from sentence_transformers import SentenceTransformer
import time
import pandas as pd
import spacy


BATCH_SIZE = 300
DIMENSION = 300  # Embeddings size
TOP_K = 3
COUNT = 500

app = FastAPI()

MILVUS_HOST = 'standalone'
MILVUS_PORT = 19530

nlp = spacy.load('en_core_web_lg')
connections.connect(host="standalone", port="19530")

#collection_test = Collection(name="test_name")

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

#collection_test.create_index(
#  field_name="vector_field",
#  index_params=index_params,
#  index_name="busroutes_index"
#)

#collection_bus_routes.load()
#collection_test.load()

# IMPORTOVANJE CSV-A
fields = [
    FieldSchema(name='id', dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name='RouteDescription', dtype=DataType.VARCHAR, max_length=1000),
    FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, dim=DIMENSION)
]
schema = CollectionSchema(fields=fields,enable_dynamic_fields=True, primary_field='id')
BusDepartCollection = Collection(name="BusDepartCollection", schema=schema)

index_params_bus = {
    'metric_type':'L2',
    'index_type':"IVF_FLAT",
    'params':{'nlist': 1536}
}

BusDepartCollection.create_index(field_name="embedding", index_params=index_params_bus)
BusDepartCollection.load()

transformer = SentenceTransformer('all-MiniLM-L6-v2')

def csv_load(file_path, encoding='utf-8'):
    with open(file_path, 'r', encoding=encoding, newline='') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            if '' in (row[3], row[3]):
                continue
            yield (row[3], row[3])


def embed_insert(data):
    #embeds = transformer.encode(data[1]) 
    print(data[1][0],"\n",data[0][0])
    print("---------------------------------------")
    doc = nlp(data[1][0])
    ins = [
            [data[0][0]],
            [doc.vector]
    ]
    BusDepartCollection.insert(ins)


data_batch = [[],[]]

count = 0

for RouteDescription,RouteDescription1 in csv_load("novi_sad_bus_departure_times.csv"):
    print(RouteDescription,RouteDescription1)
    data_batch[0].append(RouteDescription)
    data_batch[1].append(RouteDescription1)
    #if len(data_batch[0]) % BATCH_SIZE == 0:
    embed_insert(data_batch)
    data_batch = [[],[]]
    count += 1


if len(data_batch[0]) != 0:
    embed_insert(data_batch)

BusDepartCollection.flush()




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
        count = collection.num_entities
        return {"message": "Count of entities in collection", "count": count}
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
    
#docker run --name attu -p 8000:3000 -e HOST_URL=http://192.168.1.84:8000 -e MILVUS_URL=http://192.168.1.84:19530 zilliz/attu:v2.3.6 ATTU GUI ZA MILVUS
