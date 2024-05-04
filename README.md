# Smart Document Analyzer

Smart Document Analyzer is a powerful Flask and MongoDB-based web application designed to intelligently analyze and process documents. It leverages natural language processing techniques to extract, analyze, and present key insights from uploaded PDF documents, making it an invaluable tool for data analysis, research, and academic studies.

## Demo



https://github.com/JacobisEpic/Smart-Document-Analyzer/assets/108195485/8b7d659b-0434-4d90-bc65-1f4acfffc28f



## Application Screenshots

Below are various screenshots depicting the functionality and user interface of the Smart Document Analyzer:
![Screenshot 2024-05-04 at 12 14 25 AM](https://github.com/JacobisEpic/Smart-Document-Analyzer/assets/108195485/438d403e-1ef6-4186-a54c-4989922076c6)
Here is the home screen

## Authorization and Authentication
![Screenshot 2024-05-04 at 12 15 59 AM](https://github.com/JacobisEpic/Smart-Document-Analyzer/assets/108195485/3315de1a-0122-4647-80e8-b3f1624e003b)
The Password is hashed in the database

## Secure File Uploader/Ingester
![Screenshot 2024-05-04 at 12 17 10 AM](https://github.com/JacobisEpic/Smart-Document-Analyzer/assets/108195485/01f04262-ff24-43cc-9db0-7a5f381dbd39)
Here is the upload page

## Feed Ingester & Output Generator 

## Docker Setup

The project can be easily set up and run using Docker. Here are some snapshots of the application running in Docker containers:

![Docker Screenshot 1](https://github.com/JacobisEpic/Smart-Document-Analyzer/assets/108195485/a51ca726-d7d1-4e52-8bf1-59c3eaabd24c)
![Docker Screenshot 2](https://github.com/JacobisEpic/Smart-Document-Analyzer/assets/108195485/387ef4eb-e2bd-4157-a265-cbd07cec6e7c)

## Getting Started

To get started with Smart Document Analyzer, follow the instructions below:

### Prerequisites

- Docker
- Python 3.8 or higher

### Installation

1. Clone the repository:
```bash
git clone https://github.com/JacobisEpic/Smart-Document-Analyzer.git
cd Smart-Document-Analyzer

2. Run MongoDB Database
brew services start mongodb-community
note: mongosh or mongod does not work :(

