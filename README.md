# Ingest_manuals

## Introduction
Python script to ingest EV manuals into MongoDB

## Installation requirements
1. uv. Please follow the installation steps here: https://docs.astral.sh/uv/
2. Python virtual environment
3. Unstructured open source. Please refer to the installation instructions here: https://docs.unstructured.io/open-source/installation/full-installation
4. Additional libraries from requirements.txt (please use _uv add -r requirements.txt_ )
5. Mongo DB cluster credentials
6. Installation and initialization of Google Cloud SDK (please refer to instructions here: https://cloud.google.com/sdk/docs/install-sdk)

## How to run
1. Please create a .env file locally to securely store the MongoDB credentials under the variables _DB_URI_ and _MONGO_APPNAME_
2. Run the data ingest script as follows: uv run data_ingest.py _<EV model name without spaces>_ _<Publicly availabel URL of the manual pdf file>_
Please note: Chunking and generating embeddings will take time

## Solution component selection
1. Unstructured library is used since it is able to contextually generate chunks from pdfs by title
2. gemini-embedding-001 model is used for embedding using the _"QUESTION_ANSWERING"_ task type
