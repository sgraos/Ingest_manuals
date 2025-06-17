from unstructured.partition.pdf import partition_pdf

from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from unstructured.staging.base import convert_to_dict
from pymongo import MongoClient
import argparse
from dotenv import load_dotenv
import os

def return_embedding(text):
    ## Generate the embeddings using gemini-embedding-001
    MODEL_NAME = "gemini-embedding-001"
    DIMENSIONALITY = 3072
    task = "QUESTION_ANSWERING"
    model = TextEmbeddingModel.from_pretrained(MODEL_NAME)
    text_input = TextEmbeddingInput(text, task)
    embedding = model.get_embeddings([text_input], output_dimensionality=DIMENSIONALITY)
    return embedding[0].values

def chunk_pdf(pdf_file):
    ## Function to chunk the pdf file
    elements = partition_pdf(pdf_file, 
                         strategy="hi_res",
                         chunking_strategy="by_title")
    outdict = convert_to_dict(elements)
    return outdict

def extract_fields(elements):
    ## Function to extract necessary fields from the chunks and generate embeddings
    import tqdm
    cleaned_elems = []
    for i in tqdm.tqdm(range(len(elements))):
        element = elements[i]
        outdict = {}
        outdict['_id'] = element['element_id']
        # outdict['orig_elements'] = element['metadata']['orig_elements']
        outdict['page_number'] = element['metadata']['page_number']
        outdict['text'] = element['text']
        outdict['embedding'] = return_embedding(element['text'])
        cleaned_elems.append(outdict)
    return cleaned_elems

def main(pdf_url, collection_name):
    ## Open the MongoDB client
    load_dotenv()
    mongo_uri = os.getenv("DB_URI")
    mongo_app = os.getenv("MONGO_APPNAME")
    mongodb_client = MongoClient(mongo_uri, appname=mongo_app)

    ## Chunk the pdf using Unstructured Open Source
    print("1/4 Chunking pdf")
    chunk_dict = chunk_pdf(pdf_url)
    
    ## Clean the chunks and extract embeddings
    print("2/4 Cleaning data")
    cleaned_docs = extract_fields(chunk_dict)
    
    ## Upload the extracted chunks with embeddings to MongoDB
    db = mongodb_client["ev_manuals"]
    collection = db[collection_name]
    print("3/4 Uploading to MongoDB")
    collection.insert_many(cleaned_docs)

    ## Generate the vector index
    print("4/4 Generating Vector index")
    index_name = "vector_index_" + collection_name

    ## Define the new vector index

    new_index_model = {
        "name": index_name,
        "type": "vectorSearch",
        "definition": {
            "fields": [
            {
                "type": "vector",
                "path": "embedding",
                "numDimensions": 3072,
                "similarity": "cosine",
            },
            ]
        },
    }

    ## Create the vector index
    collection.create_search_index(model=new_index_model)

    print(f"✅ Vector Search Index '{index_name}' created successfully:")

    mongodb_client.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Ingest an EV manual')
    parser.add_argument('model', type=str, help='EV model name')
    parser.add_argument('url', type=str, help='URL of EV manual pdf')
    args = parser.parse_args()
    ev_model = args.model.replace(' ', '_')
    main(args.url,  ev_model)

