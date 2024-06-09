# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt 
RUN pip install --no-cache-dir fastapi uvicorn pymilvus httpx sentence_transformers
RUN pip install -U pip setuptools wheel
RUN pip install -U spacy
RUN python -m spacy download en_core_web_lg

# Copy the current directory contents into the container at /app
COPY . /app
COPY milvus_standalone.py .
COPY novi_sad_bus_departure_times.csv .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["uvicorn", "milvus_standalone:app", "--host", "0.0.0.0", "--port", "8000"]
