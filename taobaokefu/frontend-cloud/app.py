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

# 检查是否配置了 DeepSeek API（支持多种命名方式）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") or os.getenv("Deepsseek_API_KEY") or os.getenv("deepseek_api_key")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com") or os.getenv("Deepsseek_BASE_URL")

# 初始化 LangChain 相关组件
@st.cache_resource
def init_langchain():
    """初始化 LangChain 组件"""
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough
    
    if not DEEPSEEK_API_KEY:
        return None, None, None
    
    try:
        # 加载人设档案
        persona_file_path = os.path.join(os.path.dirname(__file__), 'persona.txt')
        
        if not os.path.exists(persona_file_path):
            persona_file_path = os.path.join(os.path.dirname(__file__), '..', 'persona.txt')
        
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

# 模拟订单数据（用于 Streamlit Cloud）
def get_orders():
    return [
        {
            "order_id": "TB20260520001",
            "product": "Apple iPhone 15 Pro Max",
            "price": "9999",
            "status": "已发货",
            "express": "顺丰速运",
            "tracking_no": "SF1234567890"
        },
        {
            "order_id": "TB20260519002",
            "product": "Nike Air Jordan 1 篮球鞋",
            "price": "1299",
            "status": "待发货",
            "express": "中通快递",
            "tracking_no": "-"
        },
        {
            "order_id": "TB20260518003",
            "product": "戴森V15吸尘器",
            "price": "4999",
            "status": "已签收",
            "express": "京东物流",
            "tracking_no": "JD9876543210"
        },
        {
            "order_id": "TB20260520004",
            "product": "戴森V15吸尘器",
            "price": "4999",
            "status": "运输中",
            "express": "圆通速递",
            "tracking_no": "YT5555666677"
        },
        {
            "order_id": "TB20260516005",
            "product": "海尔冰箱500L",
            "price": "5999",
            "status": "待付款",
            "express": "-",
            "tracking_no": "-"
        },
        {
            "order_id": "TB20260517006",
            "product": "小米电视65英寸",
            "price": "3999",
            "status": "已发货",
            "express": "德邦快递",
            "tracking_no": "DB1122334455"
        }
    ]

# 模拟商品数据
def get_products():
    return [
        {"name": "MacBook Pro 14寸", "price": "14999", "category": "数码产品", "stock": 50, "sales": 1250},
        {"name": "华为Mate60 Pro", "price": "6999", "category": "手机", "stock": 100, "sales": 3580},
        {"name": "iPad Pro 12.9寸", "price": "8999", "category": "平板", "stock": 80, "sales": 980},
        {"name": "索尼WH-1000XM5", "price": "2999", "category": "耳机", "stock": 200, "sales": 1850},
        {"name": "Apple Watch Ultra", "price": "6299", "category": "手表", "stock": 60, "sales": 720}
    ]

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
</style>
""", unsafe_allow_html=True)

def load_chat_history():
    try:
        if os.path.exists('chat_history.json'):
            with open('chat_history.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return [{"role": "assistant", "content": "亲，您好～欢迎光临淘宝，我是您的智能客服小秘，请问有什么可以帮到您？", "timestamp": datetime.now().isoformat()}]

def save_chat_history(messages):
    try:
        with open('chat_history.json', 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"保存聊天历史失败: {str(e)}")

def clear_chat_history():
    try:
        if os.path.exists('chat_history.json'):
            os.remove('chat_history.json')
    except Exception:
        pass
    return [{"role": "assistant", "content": "亲，您好～欢迎光临淘宝，我是您的智能客服小秘，请问有什么可以帮到您？", "timestamp": datetime.now().isoformat()}]

def export_chat_history(messages):
    export_data = []
    for msg in messages:
        role = "客服" if msg["role"] == "assistant" else "用户"
        timestamp = msg.get("timestamp", "未知时间")
        export_data.append(f"[{timestamp}] {role}: {msg['content']}")
    
    return "\n\n".join(export_data)

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

if "loading" not in st.session_state:
    st.session_state.loading = False

quick_questions = [
    "我的订单什么时候发货？",
    "如何申请退换货？",
    "商品有质量问题怎么办？",
    "优惠券怎么使用？",
    "物流信息在哪里查看？",
    "支持七天无理由退换吗？",
    "发票如何开具？",
    "商品什么时候有优惠活动？",
    "如何修改收货地址？",
    "退款需要多长时间？"
]

# 主页面
st.markdown("""
<div class="main-header">
    <h1>🛒 淘小秘 - 淘宝智能客服</h1>
    <p>专业、贴心、高效的购物向导 | 7x24小时在线服务</p>
</div>
""", unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.markdown("### ⚙️ 功能菜单")
    
    if st.button("🗑️ 清空聊天", use_container_width=True):
        st.session_state.messages = clear_chat_history()
        st.success("聊天历史已清空！")
        st.rerun()
    
    if st.button("📥 导出聊天记录", use_container_width=True):
        chat_export = export_chat_history(st.session_state.messages)
        st.download_button(
            label="💾 下载聊天记录",
            data=chat_export,
            file_name=f"淘宝客服聊天记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    st.markdown("---")
    
    st.markdown("### 📞 联系我们")
    st.markdown("""
    - **服务时间**: 7x24小时
    - **人工客服**: 9:00-21:00
    - **客服热线**: 400-800-1688
    """)
    
    st.markdown("---")
    
    st.markdown("### ℹ️ 关于淘小秘")
    st.markdown("""
    淘小秘是淘宝官方智能客服助手，
    为您提供专业、高效的购物咨询服务。
    
    **服务范围**:
    - 售前咨询
    - 订单查询
    - 售后服务
    - 活动说明
    """)

# 主内容区
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### 💡 快速提问")
    cols = st.columns(2)
    for i, question in enumerate(quick_questions):
        if cols[i % 2].button(question, key=f"quick_{i}", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": question,
                "timestamp": datetime.now().isoformat()
            })
            
            if chain:
                try:
                    with st.spinner("小秘正在思考中..."):
                        result = chain.invoke({
                            "question": question
                        })
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": result,
                            "timestamp": datetime.now().isoformat()
                        })
                except Exception as e:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"非常抱歉，服务暂时出现问题：{str(e)}",
                        "timestamp": datetime.now().isoformat()
                    })
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "非常抱歉，AI模型未配置，请联系管理员配置API密钥。",
                    "timestamp": datetime.now().isoformat()
                })
            
            save_chat_history(st.session_state.messages)
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 💬 聊天记录")
    
    chat_container = st.container()
    with chat_container:
        for idx, message in enumerate(st.session_state.messages):
            if message["role"] == "assistant":
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong style="color: rgba(255,255,255,0.8);">🤖 淘小秘</strong>
                    <p style="margin-top: 5px;">{message['content']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong style="color: #FF6B35;">👤 您</strong>
                    <p style="margin-top: 5px;">{message['content']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # 输入框
    user_input = st.chat_input("请输入您的问题...")
    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        if chain:
            try:
                with st.spinner("小秘正在思考中..."):
                    result = chain.invoke({
                        "question": user_input
                    })
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result,
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"非常抱歉，服务暂时出现问题：{str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "非常抱歉，AI模型未配置，请联系管理员配置API密钥。",
                "timestamp": datetime.now().isoformat()
            })
        
        save_chat_history(st.session_state.messages)
        st.rerun()

with col2:
    # 订单展示
    st.markdown("### 📦 我的订单")
    
    orders = get_orders()
    
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
                    
                    try:
                        with st.spinner("正在查询物流..."):
                            result = chain.invoke({
                                "persona": persona_content,
                                "question": query
                            })
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": result,
                            "timestamp": datetime.now().isoformat()
                        })
                    except Exception as e:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"查询失败: {str(e)}",
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    save_chat_history(st.session_state.messages)
                    st.rerun()
    
    st.markdown("---")
    
    # 商品展示
    st.markdown("### 🛍️ 热门商品")
    
    products = get_products()
    for product in products:
        with st.expander(f"**{product['name']}**", expanded=False):
            st.markdown(f"""
            <div class="product-card">
                <div style="color: #FF4757; font-size: 20px; font-weight: 700; margin-bottom: 8px;">
                    ¥{product['price']}
                </div>
                <div style="font-size: 13px; color: #666; margin-bottom: 5px;">
                    分类: {product['category']}
                </div>
                <div style="font-size: 13px; color: #666; margin-bottom: 5px;">
                    库存: {product['stock']}件
                </div>
                <div style="font-size: 13px; color: #FF6B35;">
                    销量: {product.get('sales', 0)}件
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"💬 咨询商品", key=f"ask_{product['name']}", use_container_width=True):
                query = f"请问{product['name']}有什么优惠活动吗？"
                st.session_state.messages.append({
                    "role": "user",
                    "content": query,
                    "timestamp": datetime.now().isoformat()
                })
                
                try:
                    with st.spinner("正在查询..."):
                        result = chain.invoke({
                            "persona": persona_content,
                            "question": query
                        })
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result,
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"咨询失败: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    })
                
                save_chat_history(st.session_state.messages)
                st.rerun()
