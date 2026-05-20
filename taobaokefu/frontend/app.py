
import chainlit as cl
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

@cl.on_chat_start
async def start():
    await cl.Message(
        content="亲，您好～欢迎光临淘宝，我是您的智能客服小秘，请问有什么可以帮到您？",
        author="淘小秘"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"question": message.content}
        )
        
        if response.status_code == 200:
            result = response.json()
            await cl.Message(
                content=result["response"],
                author="淘小秘"
            ).send()
        else:
            await cl.Message(
                content="非常抱歉，服务器暂时出现问题，请稍后再试～",
                author="淘小秘"
            ).send()
    except Exception as e:
        await cl.Message(
            content=f"非常抱歉，连接服务器时出现问题：{str(e)}",
            author="淘小秘"
        ).send()

if __name__ == "__main__":
    cl.run()
