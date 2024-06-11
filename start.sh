#!/bin/bash

# Start the first service
uvicorn milvus_standalone:app --host 0.0.0.0 --port 8000 &

# Start the second service
#python busRoutes.py &

# Start the third service
#python landmarks.py &

# Start the fourth service
#python busStops.py &

# Wait for all background processes to finish
wait