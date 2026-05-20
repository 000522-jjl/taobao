
import sys
import os
import logging
import time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
os.environ["PYTHONIOENCODING"] = "utf-8"

from fastapi import FastAPI, Response, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
import json

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('taobao_customer_service.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="淘宝AI客服 - 淘小秘",
    version="2.0",
    description="基于LangChain的淘宝智能客服系统 - 优化版"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

persona_file_path = os.path.join(os.path.dirname(__file__), '..', 'persona.txt')
try:
    with open(persona_file_path, 'r', encoding='utf-8') as f:
        persona_content = f.read()
    logger.info("人设档案加载成功")
except Exception as e:
    logger.error(f"人设档案加载失败: {str(e)}")
    persona_content = "你是淘宝AI客服淘小秘"

deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

if not deepseek_api_key:
    logger.error("DeepSeek API密钥未设置")
    raise ValueError("请在.env文件中设置DEEPSEEK_API_KEY")

try:
    llm = ChatOpenAI(
        model_name="deepseek-chat",
        openai_api_key=deepseek_api_key,
        openai_api_base=deepseek_base_url,
        temperature=0.7,
        timeout=30,
        max_retries=2
    )
    logger.info("LLM模型初始化成功")
except Exception as e:
    logger.error(f"LLM模型初始化失败: {str(e)}")
    raise

prompt = ChatPromptTemplate.from_messages([
    ("system", """
你是淘宝AI客服"淘小秘"，请根据以下人设档案进行回答：

{persona}

请严格按照以上人设档案中的规则进行回复，特别是：
1. 语气要亲切友好，使用"亲"、"您好"等礼貌用语
2. 对于淘宝购物相关的问题，请参考人设档案中的知识边界和交互规则
3. 对于超出淘宝购物范围的问题，请礼貌告知用户无法解答
4. 保持专业、耐心的态度

用户问题：
{question}
"""),
    ("user", "{question}")
])

chain = (
    RunnablePassthrough.assign(
        persona=lambda x: persona_content
    )
    | prompt
    | llm
    | StrOutputParser()
)

from pydantic import BaseModel

class ChatRequest(BaseModel):
    question: str

class FeedbackRequest(BaseModel):
    message_id: int
    rating: int
    comment: str = ""

sample_orders = [
    {
        "order_id": "TB20260520001",
        "product": "Apple iPhone 15 Pro Max",
        "price": 9999,
        "status": "已发货",
        "express": "顺丰速运",
        "tracking_no": "SF1234567890",
        "delivery_time": "预计5月22日送达",
        "image": "https://img.alicdn.com/imgextra/i4/2215305669498/O1CN01MHkPM21h4h4h4h4h4_!!2215305669498.jpg"
    },
    {
        "order_id": "TB20260519002",
        "product": "Nike Air Jordan 1 篮球鞋",
        "price": 1299,
        "status": "待发货",
        "express": "中通快递",
        "tracking_no": "-",
        "delivery_time": "48小时内发货",
        "image": "https://img.alicdn.com/imgextra/i4/2215305669498/O1CN01MHkPM21h4h4h4h4h4_!!2215305669498.jpg"
    },
    {
        "order_id": "TB20260518003",
        "product": "戴森V15吸尘器",
        "price": 4999,
        "status": "已签收",
        "express": "京东物流",
        "tracking_no": "JD9876543210",
        "delivery_time": "5月20日已签收",
        "image": "https://img.alicdn.com/imgextra/i4/2215305669498/O1CN01MHkPM21h4h4h4h4h4_!!2215305669498.jpg"
    },
    {
        "order_id": "TB20260517004",
        "product": "小米电视65英寸",
        "price": 3999,
        "status": "运输中",
        "express": "德邦快递",
        "tracking_no": "DB1122334455",
        "delivery_time": "预计5月21日送达",
        "image": "https://img.alicdn.com/imgextra/i4/2215305669498/O1CN01MHkPM21h4h4h4h4h4_!!2215305669498.jpg"
    },
    {
        "order_id": "TB20260516005",
        "product": "海尔冰箱500L",
        "price": 5999,
        "status": "待付款",
        "express": "-",
        "tracking_no": "-",
        "delivery_time": "-",
        "image": "https://img.alicdn.com/imgextra/i4/2215305669498/O1CN01MHkPM21h4h4h4h4h4_!!2215305669498.jpg"
    }
]

sample_products = [
    {"name": "MacBook Pro 14寸", "category": "数码产品", "price": 14999, "stock": 50, "sales": 1250},
    {"name": "华为Mate60 Pro", "category": "手机", "price": 6999, "stock": 100, "sales": 3580},
    {"name": "索尼WH-1000XM5耳机", "category": "音频设备", "price": 2499, "stock": 80, "sales": 890},
    {"name": "格力空调1.5匹", "category": "家电", "price": 3499, "stock": 30, "sales": 456},
    {"name": "优衣库羽绒服", "category": "服装", "price": 599, "stock": 200, "sales": 2150}
]

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    logger.info(f"请求开始 - 方法: {request.method}, 路径: {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(f"请求完成 - 状态码: {response.status_code}, 耗时: {process_time:.2f}秒")
        
        return response
    except Exception as e:
        logger.error(f"请求处理异常: {str(e)}")
        raise

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局异常: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "服务器内部错误",
            "message": "非常抱歉，服务暂时出现问题，请稍后再试～",
            "detail": str(exc) if os.getenv("DEBUG") == "true" else None
        },
        media_type="application/json; charset=utf-8"
    )

@app.get("/")
async def root():
    return JSONResponse(
        content={
            "message": "淘宝AI客服 - 淘小秘 API",
            "version": "2.0",
            "status": "running"
        },
        media_type="application/json; charset=utf-8"
    )

@app.get("/health")
async def health_check():
    try:
        llm_status = "ok" if llm else "error"
        
        return JSONResponse(
            content={
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "llm": llm_status,
                    "persona": "loaded" if persona_content else "not_loaded"
                }
            },
            media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)},
            media_type="application/json; charset=utf-8"
        )

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="问题不能为空")
        
        logger.info(f"收到用户问题: {request.question[:50]}...")
        
        start_time = time.time()
        
        result = chain.invoke({
            "persona": persona_content,
            "question": request.question
        })
        
        process_time = time.time() - start_time
        logger.info(f"LLM响应成功，耗时: {process_time:.2f}秒")
        
        return JSONResponse(
            content={
                "response": result,
                "timestamp": datetime.now().isoformat(),
                "process_time": f"{process_time:.2f}s"
            },
            media_type="application/json; charset=utf-8"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"聊天处理失败: {str(e)}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "response": "非常抱歉，服务暂时出现问题，请稍后再试～如问题持续，请联系人工客服400-800-1688",
                "error": str(e)
            },
            media_type="application/json; charset=utf-8"
        )

@app.get("/orders")
async def get_orders():
    try:
        logger.info("获取订单列表")
        return JSONResponse(
            content={"orders": sample_orders},
            media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"获取订单失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取订单失败")

@app.get("/products")
async def get_products():
    try:
        logger.info("获取商品列表")
        return JSONResponse(
            content={"products": sample_products},
            media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"获取商品失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取商品失败")

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    try:
        logger.info(f"收到用户反馈 - 消息ID: {request.message_id}, 评分: {request.rating}")
        
        return JSONResponse(
            content={
                "message": "感谢您的反馈！我们会持续改进服务质量～",
                "feedback_id": f"FB{int(time.time())}"
            },
            media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"反馈提交失败: {str(e)}")
        raise HTTPException(status_code=500, detail="反馈提交失败")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("启动淘宝AI客服服务...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
