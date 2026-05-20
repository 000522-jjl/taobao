
import streamlit as st
import requests
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")

st.set_page_config(
    page_title="淘小秘 - 淘宝AI客服",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        border: 2px solid #FF6B35;
        border-radius: 20px;
    }
    
    section[data-testid="stChatMessage"] {
        background: transparent;
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

def get_orders_from_backend():
    try:
        response = requests.get(f"{BACKEND_URL}/orders", timeout=5)
        if response.status_code == 200:
            return response.json()["orders"]
    except Exception:
        pass
    return []

def get_products_from_backend():
    try:
        response = requests.get(f"{BACKEND_URL}/products", timeout=5)
        if response.status_code == 200:
            return response.json()["products"]
    except Exception:
        pass
    return []

def send_feedback(message_id, rating, comment=""):
    try:
        response = requests.post(
            f"{BACKEND_URL}/feedback",
            json={"message_id": message_id, "rating": rating, "comment": comment},
            timeout=5
        )
        return response.status_code == 200
    except Exception:
        return False

if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

if "loading" not in st.session_state:
    st.session_state.loading = False

if "show_feedback" not in st.session_state:
    st.session_state.show_feedback = {}

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

st.markdown("""
<div class="main-header">
    <h1>🛒 淘小秘 - 淘宝智能客服</h1>
    <p>专业、贴心、高效的购物向导 | 7x24小时在线服务</p>
</div>
""", unsafe_allow_html=True)

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
            
            try:
                with st.spinner("小秘正在思考中..."):
                    response = requests.post(
                        f"{BACKEND_URL}/chat",
                        json={"question": question},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": result["response"],
                            "timestamp": datetime.now().isoformat()
                        })
                    else:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "非常抱歉，服务器暂时出现问题，请稍后再试～如问题持续，请联系人工客服400-800-1688",
                            "timestamp": datetime.now().isoformat()
                        })
            except requests.exceptions.Timeout:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "抱歉，请求超时了，请稍后再试～",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"非常抱歉，连接服务器时出现问题：{str(e)}",
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
                    <div style="display: flex; align-items: flex-start;">
                        <div style="font-size: 24px; margin-right: 10px;">🤖</div>
                        <div style="flex: 1;">
                            <div style="font-weight: 500; margin-bottom: 5px;">淘小秘</div>
                            <div>{message['content']}</div>
                            <div style="font-size: 11px; opacity: 0.8; margin-top: 5px;">
                                {message.get('timestamp', '')[:19]}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message user-message">
                    <div style="display: flex; align-items: flex-start; justify-content: flex-end;">
                        <div style="flex: 1; text-align: right;">
                            <div style="font-weight: 500; margin-bottom: 5px;">我</div>
                            <div>{message['content']}</div>
                            <div style="font-size: 11px; opacity: 0.6; margin-top: 5px;">
                                {message.get('timestamp', '')[:19]}
                            </div>
                        </div>
                        <div style="font-size: 24px; margin-left: 10px;">👤</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    user_input = st.chat_input("请输入您的问题...")
    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        try:
            with st.spinner("小秘正在思考中..."):
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"question": user_input},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["response"],
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "非常抱歉，服务器暂时出现问题，请稍后再试～如问题持续，请联系人工客服400-800-1688",
                        "timestamp": datetime.now().isoformat()
                    })
        except requests.exceptions.Timeout:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "抱歉，请求超时了，请稍后再试～",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"非常抱歉，连接服务器时出现问题：{str(e)}",
                "timestamp": datetime.now().isoformat()
            })
        
        save_chat_history(st.session_state.messages)
        st.rerun()

with col2:
    orders = get_orders_from_backend()
    
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
                        
                        try:
                            response = requests.post(
                                f"{BACKEND_URL}/chat",
                                json={"question": query},
                                timeout=30
                            )
                            if response.status_code == 200:
                                result = response.json()
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": result["response"],
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
    else:
        st.info("暂无订单信息")
    
    st.markdown("---")
    
    products = get_products_from_backend()
    
    st.markdown("### 🛍️ 热门商品")
    if products:
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
                        response = requests.post(
                            f"{BACKEND_URL}/chat",
                            json={"question": query},
                            timeout=30
                        )
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": result["response"],
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
    else:
        st.info("暂无商品信息")

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #666;">
    <p style="margin: 0;">© 2024 淘小秘 - 淘宝智能客服 | 您的贴心购物助手</p>
    <p style="margin: 5px 0 0 0; font-size: 12px;">基于LangChain框架开发 | DeepSeek大模型驱动</p>
</div>
""", unsafe_allow_html=True)
