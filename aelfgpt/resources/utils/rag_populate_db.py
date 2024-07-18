__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


import os, torch, sys, logging
from dotenv import find_dotenv, dotenv_values
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext
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

llm_url = config.get("AELFGPT_LLM_URL")
chroma_host = config.get("AELFGPT_CHROMA_HOST")
chroma_port = config.get("AELFGPT_CHROMA_PORT")
print(
    f"llm_url: {llm_url}\nchroma_host: {chroma_host}\nchroma_port: {chroma_port}"
)

# create client and a new collection
remote_db = chromadb.HttpClient(host=chroma_host, port=chroma_port)
docs_collection = remote_db.get_or_create_collection("docs")

# LlamaIndex will download embeddings models as needed
# Set llamaindex cache dir to ../cache dir here (Default is system tmp)
# This way, we can easily see downloaded artifacts
os.environ['LLAMA_INDEX_CACHE_DIR'] = os.path.join(os.path.abspath('../'), 'cache')

""" Setup Embeddings """

llm = Ollama(model="codeqwen", request_timeout=60.0, base_url=llm_url)
Settings.llm = llm
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.embed_model = embed_model
vector_store = ChromaVectorStore(chroma_collection=docs_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

""" Read JSON Documents """

json_data_file = './aelfgpt/resources/aelfdocs.json'
json_docs = JSONReader(levels_back=0).load_data(json_data_file)

print (f"Loaded {len(json_docs)} chunks from '{json_data_file}'")

""" Index the Documents and Store Them Into MongoDB Atlas """

json_index = VectorStoreIndex.from_documents(
    json_docs,
    storage_context=storage_context,
    embed_model=embed_model
)