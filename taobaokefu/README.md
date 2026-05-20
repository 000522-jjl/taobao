
# 淘小秘 - 淘宝AI客服

基于LangChain框架开发的淘宝智能客服系统，体现大模型应用开发的核心要素：LLM调用、Prompt工程、Chain链式调用、Memory记忆、Tool工具使用。

## 项目结构

```
taobaokefu/
├── persona.txt           # 客服人设档案
├── backend/              # 后端服务（LangServe）
│   ├── main.py          # 主服务文件
│   ├── requirements.txt # 依赖列表
│   └── .env             # 环境变量配置
├── frontend/             # Chainlit前端
│   ├── app.py           # 前端应用
│   ├── requirements.txt # 依赖列表
│   └── .env             # 环境变量配置
├── frontend-streamlit/   # Streamlit前端（带链条功能）
│   ├── app.py           # 前端应用
│   ├── requirements.txt # 依赖列表
│   └── .env             # 环境变量配置
└── README.md            # 项目说明文档
```

## 快速开始

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
cd backend
python main.py
```

后端服务将在 http://localhost:8000 启动。

### 3. 启动前端（Chainlit版本）

打开新终端：

```bash
cd frontend
pip install -r requirements.txt
chainlit run app.py
```

### 4. 启动前端（Streamlit版本）

打开新终端：

```bash
cd frontend-streamlit
pip install -r requirements.txt
streamlit run app.py
```

## 功能特性

- **智能客服对话**：基于DeepSeek大模型实现智能问答
- **记忆功能**：支持对话历史记忆
- **人设驱动**：根据预设的客服人设档案进行响应
- **多前端支持**：提供Chainlit和Streamlit两种前端方案
- **RESTful API**：后端提供标准的API接口

## 客服人设档案

客服人设档案包含以下内容：
- **身份定位**：角色定位、核心使命
- **语气风格**：基本语气、用语规范、禁忌用语
- **知识边界**：可解答范围、不可解答范围、边界处理原则
- **交互规则**：响应时效、沟通流程、问题处理优先级、投诉处理规则
- **常用话术模板**：售前咨询、订单查询、售后服务、活动说明
- **服务禁忌**：行为禁忌、内容禁忌
- **服务标准**：服务目标、服务承诺

## API接口

### POST /chat

发起客服对话

**请求体：**
```json
{
  "question": "用户问题内容"
}
```

**响应：**
```json
{
  "response": "客服回复内容"
}
```

## 技术栈

- **后端**：FastAPI + LangChain + LangServe
- **前端**：Chainlit / Streamlit
- **大模型**：DeepSeek API
- **记忆机制**：ConversationBufferMemory

## 注意事项

1. 确保已配置有效的DeepSeek API Key
2. 后端服务启动后才能访问前端
3. 建议使用Python 3.10+版本
