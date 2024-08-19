**Public Transportation Chatbot**

Project Overview :
This project involves the development of a chatbot designed to answer questions related to public transportation, such as bus schedules, stop locations, and nearby landmarks. The chatbot queries a vector database (Milvus) to retrieve relevant information and also interacts with a Spring application and a relational database to provide accurate and comprehensive answers.

Features :
 - Vector Search: The chatbot utilizes a vector database (Milvus) to perform semantic search, enabling it to understand and respond to complex user queries.
 - Multi-Source Data Retrieval: In addition to the vector database, the chatbot communicates with a Spring application that interfaces with a relational database to gather detailed information about bus routes, schedules, and landmarks.
 - Domain-Specific Expertise: The chatbot is tailored specifically for public transportation, making it highly effective at answering questions related to bus stops, schedules, and nearby points of interest.
Technologies :
 - Python: The primary language used for developing the chatbot logic and vector database queries.
 - Milvus: A vector database used for semantic search, enabling the chatbot to understand and respond to user queries.
 - Java Spring: Used to build the backend application that the chatbot communicates with for additional data retrieval.
 - Relational Database: Stores structured data such as bus schedules, routes, and landmark information.
