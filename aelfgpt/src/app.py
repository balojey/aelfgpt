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
from langchain_community.chat_models import ChatOllama as SQLChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig


# Setup logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# Load Settings
sys.path.insert(0, '../')
config = dotenv_values(find_dotenv())

llm_url = config.get("AELFGPT_LLM_URL")
llm_name = config.get("AELFGPT_LLM_NAME")
atlas_uri = config.get("ATLAS_URI")
db_url = config.get("DB_URL")

if not all([llm_url, atlas_uri, llm_name, db_url]):
    logging.error("Environment variables AELFGPT_LLM_URL, AELFGPT_LLM_NAME, DB_URL, or ATLAS_URI are not set.")

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
    db = SQLDatabase.from_uri(str(db_url))
except Exception as e:
    logging.error("Error loading in db: ", e)


@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="THORIN",
            markdown_description="The only assistant you need for coding, reading the docs and debugging your smart contracts.",
            icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRhJs1XadNtYiSVs2xcCjo3sDqdYktRNgAqHQ&s",
        ),
        cl.ChatProfile(
            name="GANDALF",
            markdown_description="This model helps you gain insight from on-chain data on the aelf blockchain.",
            icon="https://pbs.twimg.com/media/EM_VsGXWoAALfFz.jpg",
        ),
    ]



@cl.on_chat_start
async def start():
    llm = Ollama(model=llm_name, request_timeout=120.0, base_url=llm_url)
    Settings.llm = llm
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    Settings.context_window = 4096

    Settings.callback_manager = CallbackManager([cl.LlamaIndexCallbackHandler()])
    thorin = index.as_chat_engine(
        chat_mode="context",
        system_prompt=(
                """
                You're a helpful assistant who help developers understand the aelf blockchain documentation better, \
                a smart contract debugger who checks smart contracts written for the aelf blockchain for errors, \
                and a smart contract generator for the aelf blockchain.
                Your name is Thorin.
                """
        ),
        memory=ChatMemoryBuffer.from_defaults()
    )

    llm = SQLChatModel(model=llm_name, request_timeout=120.0)
    gandalf = create_sql_agent(
        llm, db=db, agent_type="openai-tools", verbose=True,
        callback_manager=[cl.LangchainCallbackHandler()]
        )

    chat_profile = cl.user_session.get("chat_profile")
    cl.user_session.set("thorin", thorin)
    cl.user_session.set("gandalf", gandalf)

    await cl.Message(
        author="Assistant", content=f"Hello! Im an {chat_profile}. How may I help you?"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    chat_profile = cl.user_session.get("chat_profile")
    if chat_profile == "THORIN":
        thorin: BaseChatEngine = cl.user_session.get("thorin")
        msg = cl.Message(content="", author="Assistant")

        res: ChatResponseAsyncGen = await thorin.achat(message=message.content)
        res.is_dummy_stream = True

        for token in res.response_gen:
            await msg.stream_token(token)
        await msg.send()
    else:
        gandalf = cl.user_session.get("gandalf")
        msg = cl.Message(content="")

        for chunk in gandalf.invoke(message.content)["output"]:
            await msg.stream_token(chunk)
        await msg.send()