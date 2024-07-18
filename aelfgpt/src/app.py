import sys
import os
import torch
import logging
from dotenv import find_dotenv, dotenv_values
import chromadb

# Import and set up pysqlite3
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError as e:
    logging.error("pysqlite3 import error: ", e)

# Import chainlit and llama_index
try:
    import chainlit as cl
    from llama_index.llms.ollama import Ollama
    from llama_index.core.llms import ChatMessage, ChatResponse, ChatResponseAsyncGen
    from llama_index.core.memory import ChatMemoryBuffer
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.core import StorageContext, VectorStoreIndex, Settings
    from llama_index.readers.json import JSONReader
    from llama_index.vector_stores.chroma import ChromaVectorStore
except ImportError as e:
    logging.error("Error importing modules: ", e)

# Setup logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# Load Settings
sys.path.insert(0, '../')
config = dotenv_values(find_dotenv())

llm_url = config.get("AELFGPT_LLM_URL")
chroma_host = config.get("AELFGPT_CHROMA_HOST")
chroma_port = config.get("AELFGPT_CHROMA_PORT")
llm_name = config.get("AELFGPT_LLM_NAME")

if not all([llm_url, chroma_host, chroma_port, llm_name]):
    logging.error("Environment variables AELFGPT_LLM_URL, AELFGPT_LLM_NAME, AELFGPT_CHROMA_HOST, or AELFGPT_CHROMA_PORT are not set.")
    sys.exit(1)

try:
    # Create ChromaDB client and collection
    remote_db = chromadb.HttpClient(host=chroma_host, port=chroma_port)
    docs_collection = remote_db.get_collection("docs")
except Exception as e:
    logging.error("Error connecting to ChromaDB: ", e)
    sys.exit(1)

# Setup Embeddings
try:
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    Settings.embed_model = embed_model
except Exception as e:
    logging.error("Error setting up HuggingFaceEmbedding: ", e)
    sys.exit(1)

# Setup LLM and VectorStore
try:
    llm = Ollama(model=llm_name, request_timeout=60.0, base_url=llm_url)
    Settings.llm = llm
    vector_store = ChromaVectorStore(chroma_collection=docs_collection)
except Exception as e:
    logging.error("Error setting up LLM or VectorStore: ", e)
    sys.exit(1)

# Setup VectorStoreIndex and ChatEngine
try:
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        llm=llm,
        system_prompt=(
            """
            You're a RAG-Enabled LLM for the aelf blockchain documentation, \
            a smart contract debugger on the aelf blockchain, \
            and a natural language smart contract generator for the aelf blockchain.
            Your name is AelfGPT.
            """
        )
    )
except Exception as e:
    logging.error("Error setting up VectorStoreIndex or ChatEngine: ", e)
    sys.exit(1)

@cl.on_message
async def main(message: cl.Message):
    try:
        response = await chat_engine.achat(message=message.content)
        response.is_dummy_stream = True
        print(f"\n\nresponse: {response}\n\n")
        msg = cl.Message(content="", author="AelfGPT")

        # Send a response back to the user
        for token in response.response_gen:
            await msg.stream_token(token=token)
        await msg.send()
    except Exception as e:
        logging.error("Error in on_message: ", e)
        msg = cl.Message(content="An error occurred while processing your request.", author="AelfGPT")
        await msg.send()
