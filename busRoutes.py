from pymilvus import connections, utility, MilvusException, MilvusClient, Collection, FieldSchema, CollectionSchema, DataType
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import csv
#from sentence_transformers import SentenceTransformer
import time
import pandas as pd
import spacy


BATCH_SIZE = 300
DIMENSION = 300  # Embeddings size


nlp = spacy.load('en_core_web_lg')
connections.connect(host="standalone", port="19530")

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
