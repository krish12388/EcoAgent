"""FastAPI application for EcoAgent."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from agents.campus_graph import CampusAgentGraph
from api.routes import campus, analysis, simulation, mock_analysis, chat
from api.data_service import DataService
from api import dependencies
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application lifecycle."""
    print("🚀 Starting EcoAgent Backend...")
    
    # Initialize data service
    data_service = DataService()
    await data_service.load_campus_data()
    dependencies.set_data_service(data_service)
    
    # Initialize campus agent graph (but don't create agents yet)
    campus_graph = CampusAgentGraph()
    campus_data = data_service.get_campus_structure()
    campus_graph.set_campus_data(campus_data)  # Just store data, agents created on-demand
    dependencies.set_campus_graph(campus_graph)
    
    print("✅ EcoAgent Backend Ready! (Agents will be created on-demand)")
    
    yield
    
    # Cleanup
    print("👋 Shutting down EcoAgent Backend...")


# Create FastAPI app
app = FastAPI(
    title="EcoAgent API",
    description="Agentic AI system for campus sustainability management",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default + alternatives
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(campus.router, prefix="/api/campus", tags=["Campus"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
app.include_router(mock_analysis.router, tags=["Mock Demo"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "EcoAgent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "campus_initialized": dependencies.campus_graph is not None,
        "data_loaded": dependencies.data_service is not None
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
