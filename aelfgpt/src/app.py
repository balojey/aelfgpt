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
    from llama_index.core.service_context import ServiceContext
    from llama_index.core.callbacks import CallbackManager
    from llama_index.readers.json import JSONReader
    from llama_index.vector_stores.chroma import ChromaVectorStore
    from llama_index.core.indices.base import BaseChatEngine
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

# Setup VectorStore
    try:
        vector_store = ChromaVectorStore(chroma_collection=docs_collection)
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    except Exception as e:
        logging.error("Error setting up VectorStore: ", e)
        sys.exit(1)


@cl.on_chat_start
async def start():
    # Setup Embeddings
    try:
        embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        Settings.embed_model = embed_model
    except Exception as e:
        logging.error("Error setting up HuggingFaceEmbedding: ", e)
        sys.exit(1)

    # Setup LLM
    try:
        llm = Ollama(model=llm_name, request_timeout=60.0, base_url=llm_url)
        Settings.llm = llm
        Settings.context_window = 4096
        service_context = ServiceContext.from_defaults(callback_manager=CallbackManager([cl.LlamaIndexCallbackHandler()]))
    except Exception as e:
        logging.error("Error setting up LLM: ", e)
        sys.exit(1)

    # Setup ChatEngine and Memory
    try:
        memory = ChatMemoryBuffer.from_defaults()
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
            ),
            service_context=service_context,
            memory=memory
        )
        cl.user_session.set("chat_engine", chat_engine)
    except Exception as e:
        logging.error("Error setting up VectorStoreIndex or ChatEngine: ", e)
        sys.exit(1)


@cl.on_message
async def main(message: cl.Message):
    try:
        chat_engine: BaseChatEngine = cl.user_session.get("chat_engine")
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
