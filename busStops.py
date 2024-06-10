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
# stop_id,name,latitude,longitude,bus_lines,facilities,nearby_landmarks,special_features


fields = [
    FieldSchema(name='id', dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name='name', dtype=DataType.VARCHAR, max_length=1000),
    FieldSchema(name='latitude', dtype=DataType.VARCHAR, max_length=500),
    FieldSchema(name='longitude', dtype=DataType.VARCHAR, max_length=500),
    FieldSchema(name='bus_lines', dtype=DataType.VARCHAR, max_length=100),
    FieldSchema(name='facilities', dtype=DataType.VARCHAR, max_length=100),
    FieldSchema(name='nearby_landmarks', dtype=DataType.VARCHAR, max_length=100),
    FieldSchema(name='special_features', dtype=DataType.VARCHAR, max_length=100),
    FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, dim=DIMENSION)
]
schema = CollectionSchema(fields=fields,enable_dynamic_fields=True, primary_field='id')
BusStopsCollection = Collection(name="BusStopsCollection", schema=schema)

index_params_busstops = {
    'metric_type':'L2',
    'index_type':"IVF_FLAT",
    'params':{'nlist': 5}
}

BusStopsCollection.create_index(field_name="embedding", index_params=index_params_busstops)
BusStopsCollection.load()


def csv_load(file_path, encoding='utf-8'):
    with open(file_path, 'r', encoding=encoding, newline='') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            #print(row)
            if '' in (row[7], row[7]):
                continue
            yield (row[1],row[2], row[3],row[4],row[5],row[6],row[7])


def embed_insert(data):
    doc = nlp(data[6][0])
    ins = [
            [data[0][0]],
            [data[1][0]],
            [data[2][0]],
            [data[3][0]],
            [data[4][0]],
            [data[5][0]],
            [data[6][0]],
            [doc.vector]
    ]
    BusStopsCollection.insert(ins)

data_batch = [[],[],[],[],[],[],[]]

count = 0
    #stop_id,name,latitude,longitude,bus_lines,facilities,nearby_landmarks,special_features

i = 0
for name,latitude,longitude,bus_lines,facilities,nearby_landmarks,special_features in csv_load("novi_sad_bus_stops.csv"):
    data_batch[0].append(name)
    data_batch[1].append(latitude)
    data_batch[2].append(longitude)
    data_batch[3].append(bus_lines)
    data_batch[4].append(facilities)
    data_batch[5].append(nearby_landmarks)
    data_batch[6].append(special_features)
    #if len(data_batch[0]) % BATCH_SIZE == 0:
    embed_insert(data_batch)
    data_batch = [[],[],[],[],[],[],[]]
    


if len(data_batch[0]) != 0:
    embed_insert(data_batch)

BusStopsCollection.flush()
