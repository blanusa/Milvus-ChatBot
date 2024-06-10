# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn pymilvus httpx
RUN pip install -U pip setuptools wheel
RUN pip install -U spacy
RUN python -m spacy download en_core_web_lg

# Copy the current directory contents into the container at /app
COPY . /app
COPY milvus_standalone.py .
COPY novi_sad_bus_departure_times.csv .
COPY landmarks.csv .
COPY busRoutes.py .
COPY busStops.py .
COPY start.sh .



# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches

#CMD ["uvicorn", "milvus_standalone:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD ["python", "busRoutes.py"]
#CMD ["python", "landmarks.py"]
#CMD ["python", "busStops.py"]
#CMD ["uvicorn", "milvus_standalone:app", "--host", "0.0.0.0", "--port", "8000" && "python busRoutes.py && python landmarks.py && python busStops.py"]
RUN chmod +x /app/start.sh

# Set the default command to run the script
CMD ["/app/start.sh"]