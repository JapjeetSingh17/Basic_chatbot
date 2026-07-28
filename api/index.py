import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="LangGraph Agent - Vercel")

# Embedded HTML UI to guarantee Vercel serverless function never fails due to missing static files
HTML_UI = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LangGraph Agent - Human in the Loop</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
            --card-bg: rgba(30, 41, 59, 0.7);
            --card-border: rgba(255, 255, 255, 0.1);
            --user-msg: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            --bot-msg: rgba(51, 65, 85, 0.8);
            --bot-border: rgba(255, 255, 255, 0.08);
            --human-alert-bg: rgba(245, 158, 11, 0.15);
            --human-alert-border: rgba(245, 158, 11, 0.4);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent: #818cf8;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        body {
            background: var(--bg-gradient);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 1rem;
        }

        .container {
            width: 100%;
            max-width: 850px;
            height: 90vh;
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--card-border);
            border-radius: 24px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            overflow: hidden;
        }

        .header {
            padding: 1.25rem 1.75rem;
            border-bottom: 1px solid var(--card-border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(15, 23, 42, 0.4);
        }

        .header-title {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            background-color: #10b981;
            border-radius: 50%;
            box-shadow: 0 0 10px #10b981;
        }

        .header h1 {
            font-size: 1.25rem;
            font-weight: 600;
            letter-spacing: -0.02em;
        }

        .header p {
            font-size: 0.85rem;
            color: var(--text-secondary);
        }

        .badge {
            background: rgba(99, 102, 241, 0.2);
            border: 1px solid rgba(99, 102, 241, 0.4);
            color: #a5b4fc;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
        }

        .chat-box {
            flex: 1;
            padding: 1.5rem;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .chat-box::-webkit-scrollbar {
            width: 6px;
        }

        .chat-box::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 4px;
        }

        .message {
            max-width: 80%;
            padding: 0.9rem 1.25rem;
            border-radius: 18px;
            font-size: 0.95rem;
            line-height: 1.5;
            animation: fadeIn 0.25s ease-out;
            word-wrap: break-word;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.user {
            align-self: flex-end;
            background: var(--user-msg);
            color: #ffffff;
            border-bottom-right-radius: 4px;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3);
        }

        .message.bot {
            align-self: flex-start;
            background: var(--bot-msg);
            border: 1px solid var(--bot-border);
            border-bottom-left-radius: 4px;
        }

        .message.bot.human-prompt {
            background: var(--human-alert-bg);
            border: 1px solid var(--human-alert-border);
            color: #fef08a;
            box-shadow: 0 0 15px rgba(245, 158, 11, 0.15);
        }

        .input-area {
            padding: 1.25rem 1.5rem;
            border-top: 1px solid var(--card-border);
            background: rgba(15, 23, 42, 0.4);
            display: flex;
            gap: 0.75rem;
        }

        .input-area input {
            flex: 1;
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid var(--card-border);
            border-radius: 14px;
            padding: 0.85rem 1.25rem;
            color: var(--text-primary);
            font-size: 0.95rem;
            outline: none;
            transition: all 0.2s ease;
        }

        .input-area input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.2);
        }

        .input-area input::placeholder {
            color: var(--text-secondary);
        }

        .input-area button {
            background: var(--user-msg);
            color: white;
            border: none;
            border-radius: 14px;
            padding: 0 1.5rem;
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3);
        }

        .input-area button:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }

        .input-area button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .typing-indicator {
            display: none;
            align-self: flex-start;
            background: var(--bot-msg);
            border: 1px solid var(--bot-border);
            padding: 0.75rem 1.25rem;
            border-radius: 18px;
            border-bottom-left-radius: 4px;
            gap: 5px;
        }

        .typing-indicator span {
            width: 7px;
            height: 7px;
            background: var(--text-secondary);
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }

        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1.0); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-title">
                <div class="status-dot"></div>
                <div>
                    <h1>LangGraph Agent</h1>
                    <p>Human-in-the-loop assistance enabled</p>
                </div>
            </div>
            <span class="badge">Vercel Deployment</span>
        </div>

        <div class="chat-box" id="chatBox">
            <div class="message bot">
                Hello! I am your LangGraph agent. I can perform calculations or request your assistance if I need help. How can I assist you today?
            </div>
            <div class="typing-indicator" id="typingIndicator">
                <span></span><span></span><span></span>
            </div>
        </div>

        <div class="input-area">
            <input type="text" id="userInput" placeholder="Type your message..." onkeydown="if(event.key==='Enter') sendMessage()" autofocus />
            <button id="sendBtn" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const chatBox = document.getElementById('chatBox');
            const sendBtn = document.getElementById('sendBtn');
            const indicator = document.getElementById('typingIndicator');

            const text = input.value.trim();
            if (!text) return;

            // Render User Message
            const userDiv = document.createElement('div');
            userDiv.className = 'message user';
            userDiv.textContent = text;
            chatBox.insertBefore(userDiv, indicator);

            input.value = '';
            input.disabled = true;
            sendBtn.disabled = true;
            indicator.style.display = 'flex';
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });

                const data = await res.json();
                indicator.style.display = 'none';

                const botDiv = document.createElement('div');
                botDiv.className = 'message bot';
                if (data.response && data.response.includes('🤖 I need your help:')) {
                    botDiv.classList.add('human-prompt');
                }
                botDiv.textContent = data.response || 'No response';
                chatBox.insertBefore(botDiv, indicator);

            } catch (err) {
                indicator.style.display = 'none';
                const errDiv = document.createElement('div');
                errDiv.className = 'message bot';
                errDiv.style.borderColor = 'rgba(239, 68, 68, 0.4)';
                errDiv.style.background = 'rgba(239, 68, 68, 0.15)';
                errDiv.textContent = 'Error communicating with serverless function: ' + err.message;
                chatBox.insertBefore(errDiv, indicator);
            } finally {
                input.disabled = false;
                sendBtn.disabled = false;
                input.focus();
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        }
    </script>
</body>
</html>"""

# Cache compiled graph in memory for serverless warm starts
_cached_graph = None
_waiting_for_human = {"flag": False}
_config = {"configurable": {"thread_id": "vercel-session"}}


def get_graph():
    global _cached_graph
    if _cached_graph is not None:
        return _cached_graph

    from typing import Annotated
    from typing_extensions import TypedDict
    from langchain_core.tools import tool
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.graph import START, END, StateGraph
    from langgraph.graph.message import add_messages
    from langgraph.prebuilt import ToolNode, tools_condition
    from langgraph.types import Command, interrupt

    class State(TypedDict):
        messages: Annotated[list, add_messages]

    @tool
    def calculator(expression: str) -> str:
        """Evaluate a basic math expression, e.g. '12 * (3 + 4)'."""
        try:
            return str(eval(expression, {"__builtins__": {}}))
        except Exception as e:
            return f"Error: {e}"

    @tool
    def human_assistance(query: str) -> str:
        """Ask the human user for help when unsure how to proceed."""
        human_response = interrupt({"query": query})
        return human_response["data"]

    tools = [calculator, human_assistance]

    # Initialize LLM safely
    groq_api_key = os.getenv("GROQ_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if groq_api_key:
        from langchain_groq import ChatGroq
        llm = ChatGroq(model_name="llama-3.1-8b-instant", groq_api_key=groq_api_key)
    elif openai_api_key:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=openai_api_key)
    else:
        try:
            from langchain_ollama import OllamaLLM
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            llm = OllamaLLM(model="llama3.1", base_url=ollama_url)
        except Exception:
            raise RuntimeError(
                "Please configure GROQ_API_KEY or OPENAI_API_KEY in your Vercel Environment Variables."
            )

    llm_with_tools = llm.bind_tools(tools)

    def chatbot(state: State):
        return {"messages": llm_with_tools.invoke(state["messages"])}

    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", ToolNode(tools=tools))
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges("chatbot", tools_condition)
    graph_builder.add_edge("tools", "chatbot")

    memory = MemorySaver()
    _cached_graph = graph_builder.compile(checkpointer=memory)
    return _cached_graph


def chat_fn(message: str):
    from langgraph.types import Command

    graph = get_graph()

    if _waiting_for_human["flag"]:
        _waiting_for_human["flag"] = False
        events = graph.stream(
            Command(resume={"data": message}), _config, stream_mode="values"
        )
    else:
        events = graph.stream(
            {"messages": [{"role": "user", "content": message}]},
            _config,
            stream_mode="values",
        )

    last_message = None
    for event in events:
        if "messages" in event:
            last_message = event["messages"][-1]

    state = graph.get_state(_config)
    if state.next:
        _waiting_for_human["flag"] = True
        pending = state.tasks[0].interrupts[0].value
        return f"🤖 I need your help: {pending['query']}"

    return last_message.content if last_message else "..."


class ChatRequest(BaseModel):
    message: str


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    try:
        response_text = chat_fn(req.message)
        return {"response": response_text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"response": f"Error: {str(e)}"})


@app.get("/", response_class=HTMLResponse)
def index():
    try:
        html_file = Path(__file__).parent.parent / "chat_agent_html.html"
        if html_file.exists():
            return html_file.read_text(encoding="utf-8")
    except Exception:
        pass
    return HTML_UI


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
