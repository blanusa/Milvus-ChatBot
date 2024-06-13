# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn pymilvus httpx reportlab
RUN pip install -U pip setuptools wheel
RUN pip install -U spacy
RUN python -m spacy download en_core_web_lg

# Copy the current directory contents into the container at /app
COPY . /app
COPY milvus_standalone.py .
COPY novi_sad_bus_departure_times.csv .
COPY insertScripts/landmarks.py /app/
COPY insertScripts/busRoutes.py /app/
COPY insertScripts/busStops.py /app/
COPY start.sh .

# Make port 8000 available to the world outside this container
EXPOSE 8000

#Function run
CMD ["uvicorn", "milvus_standalone:app", "--host", "0.0.0.0", "--port", "8000"]

#Shell run 
#RUN chmod +x /app/start.sh
#CMD ["/app/start.sh"]