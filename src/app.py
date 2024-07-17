__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


import chainlit as cl
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage, ChatResponse, ChatResponseAsyncGen
from llama_index.core.memory import ChatMemoryBuffer
import os, torch, sys, logging
from dotenv import find_dotenv, dotenv_values
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex
from llama_index.readers.json import JSONReader
from llama_index.core import Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb


# Setup logging. To see more logging, set the level to DEBUG
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

""" Load Settings """

# Change system path to root direcotry
sys.path.insert(0, '../')

# _ = load_dotenv(find_dotenv()) # read local .env file
config = dotenv_values(find_dotenv())

# create client and a new collection
db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_collection("quickstart")

# LlamaIndex will download embeddings models as needed
# Set llamaindex cache dir to ../cache dir here (Default is system tmp)
# This way, we can easily see downloaded artifacts
os.environ['LLAMA_INDEX_CACHE_DIR'] = os.path.join(os.path.abspath('../'), 'cache')

""" Setup Embedding Model """

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.embed_model = embed_model

""" Setup vector """

llm = Ollama(model="codeqwen", request_timeout=60.0, base_url="http://ollama:11434")
Settings.llm = llm
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store
)

memory = ChatMemoryBuffer.from_defaults()
chat_engine = index.as_chat_engine(
    chat_mode="context",
    memory=memory,
    system_prompt=(
        """
            You're a RAG-Enabled LLM for the aelf blockchain documentation, \
            a smart contract debugger on the aelf blockchain, \
            and a natural language smart contract generator for the aelf blockchain.
            Your name is AelfGPT.
        """
    )
)


@cl.on_message
async def main(message: cl.Message):
    response = await chat_engine.achat(message=message.content)
    response.is_dummy_stream = True
    msg = cl.Message(content="", author="AelfGPT")

    # Send a response back to the user
    for token in response.response_gen:
        await msg.stream_token(token=token)
    await msg.send()