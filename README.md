# 🤖 LangGraph Human-in-the-Loop Agent

An interactive AI chatbot built using **LangGraph**, **Groq (Llama 3.1 8B)**, and **Gradio**. This agent features a dynamic **Human-in-the-Loop (HITL)** architecture along with custom tool execution capabilities.

---

## ✨ Features

* **Groq Llama 3.1 8B Model**: Fast response times using `llama-3.1-8b-instant`.
* **Stateful Agent Workflow**: Structured graph architecture built with **LangGraph**.
* **Human-in-the-Loop Interrupts**: The agent can pause execution to ask a human user for assistance when needed.
* **Math Calculator Tool**: Evaluates mathematical expressions dynamically.
* **Interactive Web Interface**: Simple UI powered by **Gradio `ChatInterface**`.
* **Session Persistence**: In-memory checkpointing via `MemorySaver`.

---

## 🛠️ Tech Stack

* **Language**: Python 3.10+
* **Frameworks**: [LangChain](https://www.langchain.com/), [LangGraph](https://www.google.com/search?q=https://python.langchain.com/docs/langgraph/), [Gradio](https://gradio.app/)
* **LLM Provider**: [Groq](https://groq.com/) (`llama-3.1-8b-instant`)

---

## 🚀 Getting Started

### 1. Prerequisites

Make sure you have Python installed on your system. You will also need a **Groq API Key**.

### 2. Installation

Clone this repository and install the required dependencies:

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
pip install langchain-core langchain-community langgraph gradio python-dotenv langchain-groq

```

### 3. Environment Setup

Create a `.env` file in the root directory and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here

```

### 4. Run the Application

Launch the Gradio interface by running:

```bash
python main.py

```

Open the local URL provided in your terminal (usually `[http://127.0.0.1:7860](http://127.0.0.1:7860)`) in your web browser.

---

## ⚙️ How It Works

1. **User Request**: The user enters a message in the Gradio chat window.
2. **Decision Engine**: The agent evaluates the request and decides whether to respond directly or invoke a tool.
3. **Tools**:
* **`calculator`**: Runs safe basic mathematical calculations.
* **`human_assistance`**: Triggers a LangGraph `interrupt`, pausing execution until the user provides clarification or assistance via the chat.


4. **State Management**: LangGraph manages conversation state and resumes workflows smoothly after human input.
