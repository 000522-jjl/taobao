import streamlit as st
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="淘小秘 - 淘宝AI客服",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 检查是否配置了 DeepSeek API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# 检查是否有本地后端服务
USE_LOCAL_BACKEND = os.getenv("USE_LOCAL_BACKEND", "false").lower() == "true"
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")

# 初始化 LangChain 相关组件
@st.cache_resource
def init_langchain():
    """初始化 LangChain 组件"""
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.schema import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough
    
    if not DEEPSEEK_API_KEY:
        return None, None, None
    
    try:
        # 加载人设档案
        persona_file_path = os.path.join(os.path.dirname(__file__), '..', 'persona.txt')
        if not os.path.exists(persona_file_path):
            persona_file_path = os.path.join(os.path.dirname(__file__), 'persona.txt')
        
        if os.path.exists(persona_file_path):
            with open(persona_file_path, 'r', encoding='utf-8') as f:
                persona_content = f.read()
        else:
            persona_content = """你是淘宝AI客服"淘小秘"，专门为淘宝用户提供购物咨询和售后服务。

身份定位：
- 你是淘宝平台的智能客服助手
- 你的职责是帮助用户解答购物相关问题、处理订单咨询、提供售后服务等

语气风格：
- 亲切友好，使用"亲"、"您"等礼貌用语
- 称呼用户为"亲"
- 回复要温暖、专业、有耐心

知识边界：
- 淘宝购物相关：商品咨询、订单查询、物流配送、退换货政策、支付问题、促销活动等
- 对于超出购物咨询范围的问题，礼貌告知无法解答

交互规则：
- 积极主动，友好热情
- 回答简洁明了，突出重点
- 无法解答时，引导用户联系人工客服"""

        # 初始化 LLM
        llm = ChatOpenAI(
            model_name="deepseek-chat",
            openai_api_key=DEEPSEEK_API_KEY,
            openai_api_base=DEEPSEEK_BASE_URL,
            temperature=0.7,
            timeout=30,
            max_retries=2
        )
        
        # 创建提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是淘宝AI客服"淘小秘"，请根据以下人设档案进行回答：

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
        
        # 创建 Chain
        chain = (
            RunnablePassthrough.assign(
                persona=lambda x: persona_content
            )
            | prompt
            | llm
            | StrOutputParser()
        )
        
        return chain, llm, persona_content
        
    except Exception as e:
        st.error(f"LangChain 初始化失败: {str(e)}")
        return None, None, None

# 初始化 LangChain
chain, llm, persona_content = init_langchain()

# 加载样式
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap');
    
    * {
        font-family: 'Noto Sans SC', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #FF6B35 0%, #FF4757 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 28px;
        font-weight: 700;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        margin: 5px 0 0 0;
        font-size: 14px;
    }
    
    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #FF6B35 0%, #FF4757 100%);
        color: white;
        border-bottom-left-radius: 2px;
    }
    
    .user-message {
        background: #f8f9fa;
        color: #333;
        border-bottom-right-radius: 2px;
        border: 1px solid #e9ecef;
    }
    
    .quick-question-btn {
        background: white;
        border: 2px solid #FF6B35;
        color: #FF6B35;
        padding: 10px 15px;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.3s;
        font-weight: 500;
    }
    
    .quick-question-btn:hover {
        background: #FF6B35;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(255,107,53,0.3);
    }
    
    .order-card {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        transition: all 0.3s;
    }
    
    .order-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .status-badge {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
    }
    
    .status-shipped {
        background: #28a745;
        color: white;
    }
    
    .status-pending {
        background: #ffc107;
        color: #333;
    }
    
    .status-delivered {
        background: #17a2b8;
        color: white;
    }
    
    .status-transit {
        background: #007bff;
        color: white;
    }
    
    .status-unpaid {
        background: #dc3545;
        color: white;
    }
    
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255,255,255,.3);
        border-radius: 50%;
        border-top-color: #fff;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .feedback-section {
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px solid rgba(255,255,255,0.3);
    }
    
    .product-card {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        transition: all 0.3s;
    }
    
    .product-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .taobao-orange {
        color: #FF6B35;
    }
    
    .taobao-red {
        color: #FF4757;
    }
    
    div[data-testid="stSidebar"] {
        background: #f8f9fa;
    }
    
    .stButton>button {
        border-radius: 20px;
        border: 2px solid #FF6B35;
        color: #FF6B35;
        background: white;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background: #FF6B35;
        color: white;
        border-color: #FF6B35;
    }
    
    .stChatInput {
        border-radius: 20px;
    }
    
    .info-box {
        background: #e7f3ff;
        border-left: 4px solid #2196F3;
        padding: 10px;
        margin: 10px 0;
        border-radius: 4px;
    }
    
    .warning-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 10px 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.markdown("### 🛒 快捷入口")
    
    st.markdown("#### 📋 常用功能")
    quick_links = [
        ("🔍 物流查询", "查询订单物流"),
        ("💳 退款退货", "如何申请退款"),
        ("📦 订单管理", "修改订单信息"),
        ("💰 优惠咨询", "优惠券使用方法"),
        ("📞 联系客服", "联系人工客服")
    ]
    
    for icon_text, tip_text in quick_links:
        if st.button(f"{icon_text} {tip_text}", use_container_width=True, key=f"sidebar_{tip_text}"):
            st.session_state.messages.append({
                "role": "user",
                "content": tip_text,
                "timestamp": datetime.now().isoformat()
            })
            save_and_rerun()
    
    st.markdown("---")
    st.markdown("#### 💡 常见问题")
    st.markdown("""
    - 如何修改收货地址？
    - 订单什么时候发货？
    - 支持哪些支付方式？
    - 如何申请七天无理由退货？
    - 优惠券无法使用怎么办？
    """)
    
    st.markdown("---")
    st.markdown("#### 🔧 系统状态")
    if DEEPSEEK_API_KEY:
        st.success("✅ AI模型已连接")
    else:
        st.error("❌ AI模型未配置")
    
    if st.button("🗑️ 清空聊天", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "亲，您好～欢迎光临淘宝，我是您的智能客服小秘，请问有什么可以帮到您？",
            "timestamp": datetime.now().isoformat()
        }]
        save_chat_history(st.session_state.messages)
        st.rerun()

# 加载聊天历史
def load_chat_history():
    """加载聊天历史"""
    try:
        if os.path.exists('chat_history_cloud.json'):
            with open('chat_history_cloud.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return [{
        "role": "assistant",
        "content": "亲，您好～欢迎光临淘宝，我是您的智能客服小秘，请问有什么可以帮到您？",
        "timestamp": datetime.now().isoformat()
    }]

def save_chat_history(messages):
    """保存聊天历史"""
    try:
        with open('chat_history_cloud.json', 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"保存聊天历史失败: {str(e)}")

def save_and_rerun():
    """保存并重新运行"""
    save_chat_history(st.session_state.messages)
    st.rerun()

# 模拟订单数据
@st.cache_data(ttl=300)
def get_orders():
    """获取订单列表"""
    return [
        {
            "order_id": "TB202401150001",
            "product": "iPhone 15 Pro Max 256GB 钛金色",
            "price": "9999.00",
            "status": "运输中",
            "express": "顺丰速运",
            "tracking_no": "SF1234567890"
        },
        {
            "order_id": "TB202401140002",
            "product": "小米路由器 AX9000",
            "price": "599.00",
            "status": "已发货",
            "express": "中通快递",
            "tracking_no": "ZTO20240114002"
        },
        {
            "order_id": "TB202401130003",
            "product": "联想拯救者R9000P游戏本",
            "price": "8999.00",
            "status": "待发货",
            "express": "圆通速递",
            "tracking_no": "-"
        },
        {
            "order_id": "TB202401120004",
            "product": "索尼 WH-1000XM5 降噪耳机",
            "price": "2499.00",
            "status": "已签收",
            "express": "韵达快递",
            "tracking_no": "YD20240112004"
        },
        {
            "order_id": "TB202401110005",
            "product": "Apple AirPods Pro 2",
            "price": "1799.00",
            "status": "待付款",
            "express": "-",
            "tracking_no": "-"
        }
    ]

# 模拟商品数据
@st.cache_data(ttl=300)
def get_products():
    """获取商品列表"""
    return [
        {
            "name": "iPhone 15 Pro Max",
            "price": "9999",
            "sales": 25890,
            "rating": 4.9
        },
        {
            "name": "MacBook Pro 14英寸",
            "price": "15999",
            "sales": 12560,
            "rating": 4.8
        },
        {
            "name": "AirPods Pro 2",
            "price": "1799",
            "sales": 45670,
            "rating": 4.9
        },
        {
            "name": "iPad Pro 12.9英寸",
            "price": "9299",
            "sales": 18920,
            "rating": 4.8
        },
        {
            "name": "Apple Watch Ultra 2",
            "price": "5999",
            "sales": 9870,
            "rating": 4.7
        }
    ]

# 初始化聊天历史
if 'messages' not in st.session_state:
    st.session_state.messages = load_chat_history()

# 主界面
st.markdown("""
<div class="main-header">
    <h1>🛒 淘小秘 - 淘宝AI客服</h1>
    <p>基于 LangChain 和 DeepSeek 的智能客服系统 | 7x24 小时在线为您服务</p>
</div>
""", unsafe_allow_html=True)

# 快速提问按钮
st.markdown("#### 💬 猜你想问")
cols = st.columns(5)
quick_questions = [
    ("📦 物流查询", "查询我的订单物流信息"),
    ("💳 退款退货", "如何申请退款退货"),
    ("📝 订单问题", "修改收货地址"),
    ("🎫 优惠问题", "优惠券怎么使用"),
    ("❓ 其他问题", "还有什么可以帮你")
]

for i, (icon, text) in enumerate(quick_questions):
    with cols[i]:
        if st.button(f"{icon}\n{text}", use_container_width=True, key=f"quick_{i}"):
            st.session_state.messages.append({
                "role": "user",
                "content": text,
                "timestamp": datetime.now().isoformat()
            })
            save_and_rerun()

# 聊天消息显示
st.markdown("---")
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 您</strong>
                <div style="margin-top: 8px;">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 淘小秘</strong>
                <div style="margin-top: 8px;">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

# 输入框
if prompt := st.chat_input("请输入您的问题...", key="chat_input"):
    # 添加用户消息
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now().isoformat()
    })
    save_chat_history(st.session_state.messages)
    
    # 生成回复
    with st.spinner("🤔 淘小秘正在思考中..."):
        try:
            if chain:
                # 使用 LangChain 生成回复
                response = chain.invoke({
                    "question": prompt
                })
            elif USE_LOCAL_BACKEND:
                # 使用本地后端
                import requests
                resp = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"question": prompt},
                    timeout=30
                )
                if resp.status_code == 200:
                    response = resp.json()["response"]
                else:
                    response = "亲，服务暂时出现问题，请稍后再试～"
            else:
                response = "亲，AI服务暂未配置，请在 .env 文件中设置 DEEPSEEK_API_KEY 或设置 USE_LOCAL_BACKEND=true 使用本地后端服务。"
        except Exception as e:
            response = f"亲，服务出现了一点小问题，请稍后再试～错误信息：{str(e)}"
    
    # 添加助手回复
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().isoformat()
    })
    save_chat_history(st.session_state.messages)
    st.rerun()

# 订单展示
st.markdown("---")
orders = get_orders()

st.markdown("### 📦 我的订单")
if orders:
    for order in orders:
        status_class = {
            "已发货": "status-shipped",
            "待发货": "status-pending",
            "已签收": "status-delivered",
            "运输中": "status-transit",
            "待付款": "status-unpaid"
        }.get(order["status"], "status-pending")
        
        with st.expander(f"📱 {order['product']}", expanded=False):
            order_details = f"""
            <div class="order-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="font-weight: 500;">订单号: {order['order_id']}</span>
                    <span class="status-badge {status_class}">{order['status']}</span>
                </div>
                <div style="color: #FF4757; font-size: 18px; font-weight: 700; margin-bottom: 10px;">
                    ¥{order['price']}
                </div>
            """
            if order['express'] != '-':
                order_details += f"<div style='font-size: 13px; color: #666;'>快递: {order['express']}"
                if order['tracking_no'] != '-':
                    order_details += f"<br>运单号: {order['tracking_no']}"
                order_details += "</div>"
            order_details += "</div>"
            st.markdown(order_details, unsafe_allow_html=True)
            
            if order['tracking_no'] != '-':
                if st.button(f"🔍 查询物流", key=f"track_{order['order_id']}", use_container_width=True):
                    query = f"帮我查询订单号{order['order_id']}的物流信息，运单号是{order['tracking_no']}"
                    st.session_state.messages.append({
                        "role": "user",
                        "content": query,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    with st.spinner("🤔 淘小秘正在查询..."):
                        try:
                            if chain:
                                response = chain.invoke({
                                    "question": query
                                })
                            elif USE_LOCAL_BACKEND:
                                import requests
                                resp = requests.post(
                                    f"{BACKEND_URL}/chat",
                                    json={"question": query},
                                    timeout=30
                                )
                                if resp.status_code == 200:
                                    response = resp.json()["response"]
                                else:
                                    response = "亲，服务暂时出现问题，请稍后再试～"
                            else:
                                response = "亲，AI服务暂未配置，无法查询物流信息。"
                        except Exception as e:
                            response = f"亲，查询失败：{str(e)}"
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    save_chat_history(st.session_state.messages)
                    st.rerun()
else:
    st.info("暂无订单信息")

st.markdown("---")

products = get_products()

st.markdown("### 🛍️ 热门商品")
if products:
    cols = st.columns(5)
    for i, product in enumerate(products):
        with cols[i]:
            st.markdown(f"""
            <div class="product-card">
                <div style="font-weight: 500; margin-bottom: 5px;">{product['name']}</div>
                <div style="color: #FF4757; font-size: 18px; font-weight: 700;">
                    ¥{product['price']}
                </div>
                <div style="font-size: 12px; color: #666; margin-top: 5px;">
                    已售 {product['sales']} | ⭐ {product['rating']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"咨询 {product['name']}", key=f"product_{i}", use_container_width=True):
                query = f"我想咨询一下{product['name']}，请问有什么优惠吗？"
                st.session_state.messages.append({
                    "role": "user",
                    "content": query,
                    "timestamp": datetime.now().isoformat()
                })
                save_and_rerun()

# 页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🤖 淘小秘 - 淘宝AI客服系统 | 基于 LangChain 和 DeepSeek 构建</p>
    <p style="font-size: 12px;">© 2024 淘宝AI客服. 所有权利保留.</p>
</div>
""", unsafe_allow_html=True)
