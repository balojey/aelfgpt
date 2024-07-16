import chainlit as cl
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage, ChatResponse, ChatResponseAsyncGen


llm = Ollama(model="codeqwen", request_timeout=60.0, base_url="http://ollama:11434")
""

@cl.on_message
async def main(message: cl.Message):
    messages = [
            ChatMessage(
                role="system", content="""
                    You're a RAG-Enabled LLM for the aelf blockchain documentation, \
                    a smart contract debugger on the aelf blockchain, \
                    and a natural language smart contract generator for the aelf blockchain built by Balo.
                    Your name is AelfGPT.
                """
            ),
            ChatMessage(role="user", content=message.content),
        ]
    resp: ChatResponseAsyncGen = await llm.achat(messages=messages)
    msg = cl.Message(content="", author="AelfGPT")

    # Send a response back to the user
    for token in resp.message.content:
        await msg.stream_token(token=token)
    await msg.send()