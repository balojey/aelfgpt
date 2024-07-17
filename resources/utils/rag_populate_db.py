__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


import os, torch, sys, logging
from dotenv import find_dotenv, dotenv_values
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core import StorageContext
# from llama_index.core import SimpleDirectoryReader
from llama_index.core import VectorStoreIndex
from llama_index.readers.json import JSONReader
from llama_index.core import Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from llama_index.llms.ollama import Ollama


# Setup logging. To see more logging, set the level to DEBUG
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

""" Load Settings """

# Change system path to root direcotry
sys.path.insert(0, '../')

# _ = load_dotenv(find_dotenv()) # read local .env file
config = dotenv_values(find_dotenv())

# create client and a new collection
remote_db = chromadb.HttpClient(host="chromadb", port=6000)
chroma_collection = remote_db.get_or_create_collection("quickstart")


# ATLAS_URI = config.get('ATLAS_URI')

# if not ATLAS_URI:
#     raise Exception ("'ATLAS_URI' is not set.  Please set it above to continue...")
# else:
#     print("ATLAS_URI Connection string found:", ATLAS_URI)

# # Define DB variables
# DB_NAME = 'ava'
# COLLECTION_NAME = 'sui'
# INDEX_NAME = 'idx_embedding'

# LlamaIndex will download embeddings models as needed
# Set llamaindex cache dir to ../cache dir here (Default is system tmp)
# This way, we can easily see downloaded artifacts
os.environ['LLAMA_INDEX_CACHE_DIR'] = os.path.join(os.path.abspath('../'), 'cache')

# mongodb_client = pymongo.MongoClient(ATLAS_URI)

""" Clear out collection """

# database = mongodb_client[DB_NAME]
# collection = database [COLLECTION_NAME]

# doc_count = collection.count_documents (filter = {})
# print (f"Document count before delete : {doc_count:,}")

# result = collection.delete_many(filter= {})
# print (f"Deleted docs : {result.deleted_count}")

""" Setup Embeddings """

llm = Ollama(model="codeqwen", request_timeout=60.0, base_url="http://ollama:11434")
Settings.llm = llm
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.embed_model = embed_model
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

""" Read PDF Documents """

# pdf_data_dir = './ava/ava_backend/resources/pdfs'
# pdf_docs = SimpleDirectoryReader(
#         input_dir=pdf_data_dir
# ).load_data()

# print (f"Loaded {len(pdf_docs)} chunks from '{pdf_data_dir}'")

""" Read JSON Documents """

json_data_file = './resources/aelfdocs.json'
json_docs = JSONReader(levels_back=0).load_data(json_data_file)

print (f"Loaded {len(json_docs)} chunks from '{json_data_file}'")

""" Index the Documents and Store Them Into MongoDB Atlas """

# pdf_index = VectorStoreIndex.from_documents(
#     pdf_docs, 
#     storage_context=storage_context,
#     service_context=service_context,
# )

json_index = VectorStoreIndex.from_documents(
    json_docs,
    storage_context=storage_context,
    embed_model=embed_model
)