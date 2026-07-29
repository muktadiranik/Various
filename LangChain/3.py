import os
from typing import List
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_groq import ChatGroq

# Sympy imports
import sympy as sp

# Import and set User-Agent to comply with Wikimedia Policy
import wikipedia

wikipedia.set_user_agent("WikipediaChatbot/1.0 (contact@example.com)")

load_dotenv()


# FastAPI App
app = FastAPI(title="Wikipedia Chatbot")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# WebSocket Connection Manager
class ConnectionManager:

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


manager = ConnectionManager()


# Calculator Tools
@tool
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@tool
def subtract(a: float, b: float) -> float:
    """Subtract two numbers."""
    return a - b


@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


@tool
def divide(a: float, b: float):
    """Divide two numbers."""
    if b == 0:
        return "Cannot divide by zero."
    return a / b

# Sympy Tool


@tool
def solve_algebraic_equation(equation_str: str, variable: str = "x") -> str:
    """
    Solves algebraic equations symbolically using SymPy.
    Pass equation_str like 'x**2 + 2*x - 8' (assumed = 0) or 'Eq(x**2, 16)'.
    """
    try:
        var = sp.Symbol(variable)
        expr = sp.sympify(equation_str)

        if isinstance(expr, sp.Equality):
            solutions = sp.solve(expr, var)
        else:
            solutions = sp.solve(sp.Eq(expr, 0), var)

        return f"Solutions for {variable}: {solutions}"
    except Exception as e:
        return f"Error solving equation: {str(e)}"


@tool
def calculus_tool(expression: str, operation: str = "derivative", variable: str = "x") -> str:
    """
    Performs calculus operations: operation can be 'derivative' or 'integral'.
    Example expression: 'x**3 * sin(x)'
    """
    try:
        var = sp.Symbol(variable)
        expr = sp.sympify(expression)

        if operation == "derivative":
            result = sp.diff(expr, var)
        elif operation == "integral":
            result = sp.integrate(expr, var)
        else:
            return "Unsupported operation. Use 'derivative' or 'integral'."

        return f"Result of {operation} wrt {variable}: {result}"
    except Exception as e:
        return f"Calculus operation failed: {str(e)}"


# Wikipedia Tool
wiki_api = WikipediaAPIWrapper(
    top_k_results=2,
    doc_content_chars_max=2000,
)

wiki = WikipediaQueryRun(api_wrapper=wiki_api)


@tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for factual information about

    people, places, science, history, technology,
    organizations, books, movies, etc.
    """
    try:
        return wiki.run(query)
    except Exception as e:
        # Prevents API / parsing crashes from breaking the agent runtime
        return f"Error executing Wikipedia query for '{query}': {str(e)}"


# Register Tools
tools = [
    add,
    subtract,
    multiply,
    divide,
    solve_algebraic_equation,
    calculus_tool,
    wikipedia_search,
]


# LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY"),
)


# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a helpful AI assistant equipped with tools for factual lookup and mathematics.

### Tool Usage Rules:

1. **Wikipedia Tool**:
   - Use for queries regarding people, places, science, history, technology, books, movies, etc.

2. **Mathematics & Algebraic Tools**:
   - Use `solve_algebraic_equation` for solving algebraic equations, polynomial roots, or systems of equations.
   - Use `calculus_tool` for differentiation, integration, and calculus operations.
   - Use basic calculator tools (`add`, `subtract`, `multiply`, `divide`) for simple arithmetic.

### Math Formatting Guidelines:
- Before calling any SymPy/math tool, format mathematical expressions in strict Python syntax:
  - Use `**` for exponentiation (e.g., `x**2`, NOT `x^2`).
  - Use explicit multiplication `*` (e.g., `2*x`, NOT `2x`).
  - Use `sqrt(...)` for square roots.
  - Equations should be written in standard form or with `Eq(lhs, rhs)`.

Always use the appropriate tool instead of guessing mathematical calculations.
""",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


# Agent
agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5,  # Prevents runaway infinite tool-invocation loops
    handle_parsing_errors=True,
)


# Routes
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"request": request}
    )


# WebSocket Chat Route
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await manager.connect(websocket)
    chat_history = []

    try:
        while True:
            question = await websocket.receive_text()

            # Isolated execution block to protect the outer WebSocket loop
            try:
                response = await agent_executor.ainvoke(
                    {
                        "question": question,
                        "chat_history": chat_history,
                    }
                )

                answer = response.get(
                    "output", "Sorry, I could not process that request."
                )

                chat_history.append(HumanMessage(content=question))
                chat_history.append(AIMessage(content=answer))

                await manager.send_message(
                    f"AI: {answer}",
                    websocket,
                )

            except Exception as agent_err:
                # Catch internal agent/API errors and report to client without disconnecting
                print(f"Agent Error: {agent_err}")
                await manager.send_message(
                    "AI: Sorry, an error occurred while fetching a response. Please try again.",
                    websocket,
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket Connection Failure: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
