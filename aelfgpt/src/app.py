import sys
import os
import torch
import logging
import pymongo
from dotenv import find_dotenv, dotenv_values

# Import chainlit and llama_index
import chainlit as cl
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage, ChatResponse, ChatResponseAsyncGen
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.service_context import ServiceContext
from llama_index.core.callbacks import CallbackManager
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core.indices.base import BaseChatEngine

# Import langchain
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent


# Setup logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# Load Settings
sys.path.insert(0, '../')
config = dotenv_values(find_dotenv())

llm_url = config.get("AELFGPT_LLM_URL")
llm_name = config.get("AELFGPT_LLM_NAME")
atlas_uri = config.get("ATLAS_URI")

if not all([llm_url, atlas_uri, llm_name]):
    logging.error("Environment variables AELFGPT_LLM_URL, AELFGPT_LLM_NAME, or ATLAS_URI are not set.")

# LlamaIndex will download embeddings models as needed
# Set llamaindex cache dir to ../cache dir here (Default is system tmp)
# This way, we can easily see downloaded artifacts
os.environ['LLAMA_INDEX_CACHE_DIR'] = os.path.join(os.path.abspath('../'), 'cache')

# Define DB variables
DB_NAME = 'aelf'
COLLECTION_NAME = 'docs'
INDEX_NAME = 'idx_embedding'

mongodb_client = pymongo.MongoClient(atlas_uri)

try:
    # load index
    vector_store = MongoDBAtlasVectorSearch(mongodb_client = mongodb_client,
                    db_name = DB_NAME, collection_name = COLLECTION_NAME,
                    index_name  = 'idx_embedding',
                )
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
except Exception as e:
    logging.error("Error loading index: ", e)

try:
    # load db
    db = SQLDatabase.from_uri("sqlite:///Chinook.db")
except Exception as e:
    logging.error("Error loading in db: ", e)


@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="THORIN",
            markdown_description="The only assistant you need for coding, reading the docs and debugging your smart contracts.",
            icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name="GANDALF",
            markdown_description="This model helps you gain insight from on-chain data on the aelf blockchain.",
            icon="https://picsum.photos/250",
        ),
    ]



@cl.on_chat_start
async def start():
    llm = Ollama(model=llm_name, request_timeout=120.0, base_url=llm_url)
    Settings.llm = llm
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    Settings.context_window = 4096

    Settings.callback_manager = CallbackManager([cl.LlamaIndexCallbackHandler()])
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        system_prompt=(
                """
                You're a RAG-Enabled LLM for the aelf blockchain documentation, \
                a smart contract debugger on the aelf blockchain, \
                and a smart contract generator for the aelf blockchain.
                Your name is Thorin.
                """
        ),
        memory=ChatMemoryBuffer.from_defaults()
    )
    chat_profile = cl.user_session.get("chat_profile")
    cl.user_session.set("chat_engine", chat_engine)

    await cl.Message(
        author="Assistant", content=f"Hello! Im an {chat_profile}. How may I help you?"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    chat_engine: BaseChatEngine = cl.user_session.get("chat_engine")
    msg = cl.Message(content="", author="Assistant")

    res: ChatResponseAsyncGen = await chat_engine.achat(message=message.content)
    res.is_dummy_stream = True

    for token in res.response_gen:
        await msg.stream_token(token)
    await msg.send()