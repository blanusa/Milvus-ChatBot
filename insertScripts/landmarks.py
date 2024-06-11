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



def insertLandmarks(nlp): 


    BATCH_SIZE = 300
    DIMENSION = 300  # Embeddings size


    #nlp = spacy.load('en_core_web_lg')
    connections.connect(host="standalone", port="19530")
    # Landmark,City,Region,NumberOfCitizens

    fields = [
        FieldSchema(name='id', dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name='Landmark', dtype=DataType.VARCHAR, max_length=1000),
        FieldSchema(name='City', dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name='Region', dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name='NumberOfCitizens', dtype=DataType.INT64),
        FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, dim=DIMENSION)
    ]
    schema = CollectionSchema(fields=fields,enable_dynamic_fields=True, primary_field='id')
    LandmarkCollection = Collection(name="LandmarkCollection", schema=schema)

    index_params_landmark = {
        'metric_type':'L2',
        'index_type':"IVF_FLAT",
        'params':{'nlist': 5}
    }

    LandmarkCollection.create_index(field_name="embedding", index_params=index_params_landmark)
    LandmarkCollection.load()


    def csv_load(file_path, encoding='utf-8'):
        with open(file_path, 'r', encoding=encoding, newline='') as file:
            reader = csv.reader(file, delimiter=',')
            next(reader)
            for row in reader:
                if '' in (row[0], row[0]):
                    continue
                yield (row[0],row[1],row[2], row[3])


    def embed_insert(data):
        doc = nlp(data[0][0])
        ins = [
                [data[0][0]],
                [data[1][0]],
                [data[2][0]],
                [data[3][0]],
                [doc.vector]
        ]
        LandmarkCollection.insert(ins)

    data_batch = [[],[],[],[],[]]

    count = 0
        #Landmark,City,Region,NumberOfCitizens

    i = 0
    for Landmark,City,Region,NumberOfCitizens in csv_load("landmarks.csv"):
        data_batch[0].append(Landmark)
        data_batch[1].append(City)
        data_batch[2].append(Region)
        data_batch[3].append(int(NumberOfCitizens))
        data_batch[4].append(Landmark)
        #if len(data_batch[0]) % BATCH_SIZE == 0:
        embed_insert(data_batch)
        data_batch = [[],[],[],[],[]]
        


    if len(data_batch[0]) != 0:
        embed_insert(data_batch)

    LandmarkCollection.flush()
