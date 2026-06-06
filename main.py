from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent.agentic_workflow import GraphBuilder
from utils.save_to_document import save_document
from exception.exception import AppException, app_exception_handler
from logger.logger import get_logger
import os
import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, validator
load_dotenv()

logger = get_logger("trip_planner")

# Initialize FastAPI application
app = FastAPI()

# Production-ready CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


app.add_exception_handler(AppException, app_exception_handler)

@app.get("/health")
async def health_check():
    """Health check endpoint for production readiness."""
    return {"status": "ok", "timestamp": datetime.datetime.utcnow().isoformat() + "Z"}

class QueryRequest(BaseModel):
    question: str

    @validator("question")
    def validate_question(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Question must not be empty")
        if len(cleaned) < 10:
            raise ValueError("Question must be at least 10 characters long")
        return cleaned

# API endpoint for trip planning queries
@app.post("/query")
async def query_travel_agent(query: QueryRequest):
    """Handle incoming trip planning requests from the frontend."""
    try:
        logger.info("Received query: %s", query.question)

        # Build the agent graph and invoke the LLM with tools
        graph = GraphBuilder(model_provider="groq")
        react_app = graph()

        # Save graph visualization for debugging and development
        png_graph = react_app.get_graph().draw_mermaid_png()
        with open("my_graph.png", "wb") as f:
            f.write(png_graph)

        logger.info("Graph saved as 'my_graph.png' in %s", os.getcwd())

        # Invoke the graph with the user's query
        messages = {"messages": [query.question]}
        output = react_app.invoke(messages)

        # Extract final answer from graph output
        if isinstance(output, dict) and "messages" in output:
            final_output = output["messages"][-1].content
        else:
            final_output = str(output)

        # Save the result document
        saved_file = save_document(final_output)

        return {
            "answer": final_output,
            "saved_file": saved_file,
        }
    except Exception as e:
        logger.exception("Failed to process query")
        raise AppException(str(e))
