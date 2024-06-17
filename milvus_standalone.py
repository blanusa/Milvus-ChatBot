import datetime
from pymilvus import connections, utility, MilvusException, MilvusClient, Collection
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import spacy
from datetime import datetime
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter



from controllers.BusRoutesCollectionController import BusRouteDelete, BusRouteInsert, BusRouteSearch, BusRouteUpsert, DeleteBusRoute, InsertToBusRoutes, SearchBusRoutes, UpsertBusRoute
from controllers.BusStopsCollectionController import BusStopDelete, BusStopInsert, BusStopSearch, BusStopUpsert, DeleteBusStopEntity, InsertToBusStops, SearchBusStopText, UpsertBusStopEntity
from controllers.DTO import DeleteText, GetEntityCount, Insert, Querry, SearchLandmarks, SearchRoutes1, SearchRoutes2, SearchRoutes3, SearchStops1, SearchStops2, SearchStops3, SearchText, TestMilvusCollection, Update, Search, Delete, UpsertText, getAllCollection, insertInTextCollection
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

def draw_wrapped_text(canvas, text, x, y, max_width):
    """Draws text on the canvas, wrapping lines that exceed max_width."""
    lines = []
    words = text.split()
    current_line = ""
    for word in words:
        if canvas.stringWidth(current_line + " " + word) < max_width:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    for line in lines:
        canvas.drawString(x, y, line.strip())
        y -= 12  # Adjust line height based on your preferred spacing
    return y

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
    
# <<<<<<=============================================Report=============================================>>>>>>
@app.post("/generateReport")
async def searchCollections(body: Querry):
    try:
        collection_name = body.collection[0]
        collection = Collection(collection_name)
        res = collection.query(
            expr = body.querry[0],
            offset = body.offset,
            limit = body.numberofresults, 
            output_fields = body.outputFields,
        )
        print(res)
        NoviSad = []
        Belgrade = []
        for document in res:
            if document["City"] == "Novi Sad": 
                NoviSad.append(document)
            if document["City"] == "Belgrade":
                Belgrade.append(document)
        
        canvas = Canvas("Report.pdf", pagesize=letter)
        width, height = letter
        margin = 50
        max_width = width - 2 * margin

        y_position = height - 50
        canvas.drawString(margin, y_position, "Landmark Statistics")
        y_position -= 30
        
        canvas.drawString(margin, y_position, "Novi Sad:")
        y_position -= 20
        for doc in NoviSad[:3]:
            y_position = draw_wrapped_text(canvas, str(doc), margin, y_position, max_width)
            y_position -= 5  # Space between entries
        
        y_position -= 20  # Additional space between cities
        canvas.drawString(margin, y_position, "Belgrade:")
        y_position -= 20
        for doc in Belgrade[:3]:
            y_position = draw_wrapped_text(canvas, str(doc), margin, y_position, max_width)
            y_position -= 5  # Space between entries

        search_landmarks_body = SearchLandmarks(
                landmark=["Danube"],
                region="Vojvodina",
                min_citizens=5000,
                max_citizens=1500000
            )
        complex_res_landmarks = await searchLandmarks1(search_landmarks_body)
        print("NIGGUHHHHHH")
        y_position -= 20
        canvas.drawString(margin, y_position, "Landmarks associated with 'Danube' ")
        y_position -= 20
        for doc in complex_res_landmarks:
            y_position = draw_wrapped_text(canvas, str(doc), margin, y_position, max_width)
            y_position -= 5  

        canvas.save()
        return res
    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}
    
# <<<<<<=============================================Complex Querry=============================================>>>>>>
@app.get("/searchLandmarks1")
async def searchLandmarks1(body: SearchLandmarks):
    try:
        vectors = [nlp(name).vector for name in body.landmark]

        res = client.search(
            collection_name="LandmarkCollection",
            data=vectors,
            limit=5,
            search_params={"metric_type": "L2", "params": {"nprobe": 32, "top_k": 5}}
        )

        search_result_ids = [j["id"] for i in res for j in i]

        if not search_result_ids:
            raise HTTPException(status_code=404, detail="No search results found")

        entities = client.get(
            collection_name="LandmarkCollection",
            ids=search_result_ids
        )
        filtered_entities = []
        for entity in entities:
            if (entity["Region"].lower() == body.region.lower() and
                entity["NumberOfCitizens"] >= body.min_citizens and
                entity["NumberOfCitizens"] <= body.max_citizens):
                filtered_entities.append(entity)

        if len(filtered_entities) == 0:
            raise HTTPException(status_code=404, detail="No filtered search results found")

        returnValues = []
        for entity in filtered_entities:
            returnValues.append({
                "ID": entity["id"],
                "Landmark": entity["Landmark"],
                "City": entity["City"],
                "Region": entity["Region"],
                "NumberOfCitizens": entity["NumberOfCitizens"]
            })
        return returnValues

    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}
    
@app.get("/searchStops1")
async def searchStops1(body: SearchStops1):
    try:
        vectors = [nlp(name).vector for name in body.special_features]

        res = client.search(
            collection_name="BusStopsCollection",
            data=vectors,
            limit=5,
            search_params={"metric_type": "L2", "params": {"nprobe": 32, "top_k": 5}}
        )

        search_result_ids = [j["id"] for i in res for j in i]

        if not search_result_ids:
            raise HTTPException(status_code=404, detail="No search results found")

        entities = client.get(
            collection_name="BusStopsCollection",
            ids=search_result_ids
        )
        filtered_entities = []
        for entity in entities:
            if (
                entity["longitude"] > body.longitude and
                entity["latitude"] > body.latitude and
                body.facilities.lower() in entity["facilities"].lower()
                ):
                filtered_entities.append(entity)

        if len(filtered_entities) == 0:
            raise HTTPException(status_code=404, detail="No filtered search results found")
        returnValues = []
        for entity in filtered_entities:
            returnValues.append({
                "ID": entity["id"],
                "Name": entity["name"],
                "Latitude": str(entity["latitude"]),
                "Longitude": str(entity["longitude"]),
                "Facilities": entity["facilities"],
                "Special features": entity["special_features"]
            })
        return returnValues

    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}

@app.get("/searchStops2")
async def searchStops2(body: SearchStops2):
    try:
        vectors = [nlp(name).vector for name in body.special_features]

        res = client.search(
            collection_name="BusStopsCollection",
            data=vectors,
            limit=5,
            search_params={"metric_type": "L2", "params": {"nprobe": 32, "top_k": 5}}
        )

        search_result_ids = [j["id"] for i in res for j in i]

        if not search_result_ids:
            raise HTTPException(status_code=404, detail="No search results found")

        entities = client.get(
            collection_name="BusStopsCollection",
            ids=search_result_ids
        )
        filtered_entities = []
        for entity in entities:
            if (
                body.nearby_landmarks.lower() in entity["nearby_landmarks"].lower() and
                body.bus_lines.lower() in entity["bus_lines"].lower()
                ):
                filtered_entities.append(entity)

        if len(filtered_entities) == 0:
            raise HTTPException(status_code=404, detail="No filtered search results found")

        returnValues = []
        for entity in filtered_entities:
            returnValues.append({
                "ID": entity["id"],
                "Name": entity["name"],
                "Nearby landmarks" : entity["nearby_landmarks"],
                "Bus lines" : entity["bus_lines"],
                "Special features": entity["special_features"]
            })
        return returnValues

    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}
    
@app.get("/searchRoutes1")
async def searchRoutes1(body: SearchRoutes1):
    try:
        vectors = [nlp(name).vector for name in body.routeDescription]

        res = client.search(
            collection_name="BusDepartCollection",
            data=vectors,
            limit=5,
            search_params={"metric_type": "L2", "params": {"nprobe": 32, "top_k": 5}}
        )

        search_result_ids = [j["id"] for i in res for j in i]

        if not search_result_ids:
            raise HTTPException(status_code=404, detail="No search results found")

        entities = client.get(
            collection_name="BusDepartCollection",
            ids=search_result_ids
        )
        filtered_entities = []
        for entity in entities:
            if (
                body.street.lower() in entity["Street"].lower() and
                body.busLine.lower() in entity["BusLine"].lower()
                ):
                filtered_entities.append(entity)

        if len(filtered_entities) == 0:
            raise HTTPException(status_code=404, detail="No filtered search results found")

        returnValues = []
        for entity in filtered_entities:
            returnValues.append({
                "ID": entity["id"],
                "Street": entity["Street"],
                "BusLine" : entity["BusLine"],
                "DepartureTime" : entity["DepartureTime"],
                "RouteDescription": entity["RouteDescription"],
                "RouteDuration": entity["RouteDuration"]
            })
        return returnValues

    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}

@app.get("/searchRoutes2")
async def searchRoutes2(body: SearchRoutes2):
    try:
        vectors = [nlp(name).vector for name in body.routeDescription]

        res = client.search(
            collection_name="BusDepartCollection",
            data=vectors,
            limit=5,
            search_params={"metric_type": "L2", "params": {"nprobe": 32, "top_k": 5}}
        )

        search_result_ids = [j["id"] for i in res for j in i]

        if not search_result_ids:
            raise HTTPException(status_code=404, detail="No search results found")

        entities = client.get(
            collection_name="BusDepartCollection",
            ids=search_result_ids
        )
        filtered_entities = []
        for entity in entities:
            if (
                body.RouteDuration < entity["RouteDuration"] and
                datetime.strptime(body.DepartureTime, "%H:%M").time() > datetime.strptime(entity["DepartureTime"], "%H:%M").time()
                #body.DepartureTime.lower() in entity["DepartureTime"].lower()
                ):
                filtered_entities.append(entity)

        if len(filtered_entities) == 0:
            raise HTTPException(status_code=404, detail="No filtered search results found")

        returnValues = []
        for entity in filtered_entities:
            returnValues.append({
                "ID": entity["id"],
                "Street": entity["Street"],
                "BusLine" : entity["BusLine"],
                "DepartureTime" : entity["DepartureTime"],
                "RouteDescription": entity["RouteDescription"],
                "RouteDuration": entity["RouteDuration"]
            })
        return returnValues

    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}

@app.get("/searchRoutes3")
async def searchRoutes3(body: SearchRoutes3):
    try:
        vectors = [nlp(name).vector for name in body.routeDescription]

        res = client.search(
            collection_name="BusDepartCollection",
            data=vectors,
            limit=5,
            search_params={"metric_type": "L2", "params": {"nprobe": 32, "top_k": 5}}
        )

        search_result_ids = [j["id"] for i in res for j in i]

        if not search_result_ids:
            raise HTTPException(status_code=404, detail="No search results found")

        entities = client.get(
            collection_name="BusDepartCollection",
            ids=search_result_ids
        )
        filtered_entities = []
        for entity in entities:
            if (
                body.busLine.lower() in entity["BusLine"].lower() and
                datetime.strptime(body.departureTime, "%H:%M").time() > datetime.strptime(entity["DepartureTime"], "%H:%M").time()
                ):
                filtered_entities.append(entity)

        if len(filtered_entities) == 0:
            raise HTTPException(status_code=404, detail="No filtered search results found")

        returnValues = []
        for entity in filtered_entities:
            returnValues.append({
                "ID": entity["id"],
                "Street": entity["Street"],
                "BusLine" : entity["BusLine"],
                "DepartureTime" : entity["DepartureTime"],
                "RouteDescription": entity["RouteDescription"],
                "RouteDuration": entity["RouteDuration"]
            })
        return returnValues

    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}
    
@app.get("/searchStops3")
async def searchStops3(body: SearchStops3):
    try:
        vectors = [nlp(name).vector for name in body.special_features]

        res = client.search(
            collection_name="BusStopsCollection",
            data=vectors,
            limit=5,
            search_params={"metric_type": "L2", "params": {"nprobe": 32, "top_k": 5}}
        )

        search_result_ids = [j["id"] for i in res for j in i]

        if not search_result_ids:
            raise HTTPException(status_code=404, detail="No search results found")

        entities = client.get(
            collection_name="BusStopsCollection",
            ids=search_result_ids
        )
        filtered_entities = []
        for entity in entities:
            if (
                body.nearby_landmarks.lower() in entity["nearby_landmarks"].lower() and
                body.facilities.lower() in entity["facilities"].lower()
                ):
                filtered_entities.append(entity)

        if len(filtered_entities) == 0:
            raise HTTPException(status_code=404, detail="No filtered search results found")

        returnValues = []
        for entity in filtered_entities:
            returnValues.append({
                "ID": entity["id"],
                "Name": entity["name"],
                "Nearby landmarks" : entity["nearby_landmarks"],
                "Facilities" : entity["facilities"],
                "Special features": entity["special_features"]
            })
        return returnValues

    except Exception as e:
        return {"message": "Error occurred during Milvus connection:", "error": str(e)}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
#docker run --name attu -p 8000:3000 -e HOST_URL=http://192.168.78.220:8000 -e MILVUS_URL=http://192.168.78.220:19530 zilliz/attu:v2.3.6
