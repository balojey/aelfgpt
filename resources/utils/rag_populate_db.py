import os, torch, logging, pymongo, sys
from dotenv import find_dotenv, dotenv_values
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex
from llama_index.readers.json import JSONReader
from llama_index.core import Settings
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core import SimpleDirectoryReader


# Setup logging. To see more logging, set the level to DEBUG
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

""" Load Settings """

# Change system path to root direcotry
sys.path.insert(0, '../')

# _ = load_dotenv(find_dotenv()) # read local .env file
config = dotenv_values(find_dotenv())

ATLAS_URI = config.get('ATLAS_URI')

if not ATLAS_URI:
    raise Exception ("'ATLAS_URI' is not set.  Please set it above to continue...")
else:
    print("ATLAS_URI Connection string found:", ATLAS_URI)

# Define DB variables
DB_NAME = 'aelf'
COLLECTION_NAME = 'docs'
INDEX_NAME = 'idx_embedding'

# LlamaIndex will download embeddings models as needed
# Set llamaindex cache dir to ../cache dir here (Default is system tmp)
# This way, we can easily see downloaded artifacts
os.environ['LLAMA_INDEX_CACHE_DIR'] = os.path.join(os.path.abspath('../'), 'cache')

mongodb_client = pymongo.MongoClient(ATLAS_URI)

""" Clear out collection """

database = mongodb_client[DB_NAME]
collection = database[COLLECTION_NAME]

doc_count = collection.count_documents (filter = {})
print (f"Document count before delete : {doc_count:,}")

result = collection.delete_many(filter= {})
print (f"Deleted docs : {result.deleted_count}")

""" Setup Embeddings """

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.embed_model = embed_model
Settings.context_window = 4096
vector_store = MongoDBAtlasVectorSearch(mongodb_client = mongodb_client,
                    db_name = DB_NAME, collection_name = COLLECTION_NAME,
                    index_name  = 'idx_embedding',
                )
storage_context = StorageContext.from_defaults(vector_store=vector_store)

""" Read JSON Documents """

json_data_file = './resources/aelfdocs.json'
code_file = './resources/csharp.json'
whitepaper_data_dir = './resources'


json_docs = JSONReader(levels_back=0).load_data(json_data_file)
code_docs = JSONReader(levels_back=0).load_data(code_file)
whitepaper_docs = SimpleDirectoryReader(
        input_dir=whitepaper_data_dir
).load_data()

print (f"Loaded {len(whitepaper_docs)} chunks from '{whitepaper_data_dir}'")

print (f"Loaded {len(json_docs)} chunks from '{json_data_file}'")
print (f"Loaded {len(code_docs)} chunks from '{code_file}'")

""" Index the Documents and Store Them Into MongoDB Atlas """

json_index = VectorStoreIndex.from_documents(
    json_docs,
    storage_context=storage_context,
    embed_model=embed_model
)

code_index = VectorStoreIndex.from_documents(
    code_docs,
    storage_context=storage_context,
    embed_model=embed_model
)

whitepaper_index = VectorStoreIndex.from_documents(
    whitepaper_docs, 
    storage_context=storage_context,
    embed_model=embed_model
)