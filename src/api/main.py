from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from reportfindingrefiner.config import (
    DEFAULT_MODEL,
    DEFAULT_DB_PATH,
    DEFAULT_TABLE_NAME
)

# Import routers
from .routers import (
    search_router,
    report_router,
    finding_model_router,
    llm_router
)

# Import DB setup functions
from .db_setup import initialize_databases, process_initial_reports

# Initialize FastAPI app
app = FastAPI(
    title="Report Finding Refiner API",
    description="API for searching reports and generating finding models",
    version="1.0.0"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search_router.router, prefix="/search", tags=["search"])
app.include_router(report_router.router, prefix="/reports", tags=["reports"])
app.include_router(finding_model_router.router, prefix="/findingmodel", tags=["finding-models"])
app.include_router(llm_router.router, prefix="/llm", tags=["llm"])

@app.on_event("startup")
async def startup_event():
    """Initialize databases and process initial reports on startup"""
    print("\n🚀 Starting Report Finding Refiner API")
    
    try:
        # Initialize databases
        reports_db, findings_db = initialize_databases()
        
        # Process initial reports if any
        fragment_count = process_initial_reports()
        
        print("\n✨ Startup complete!\n")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Startup cancelled by user")
        raise
    except Exception as e:
        print(f"\n❌ Error during startup: {str(e)}")

@app.get("/")
def read_root():
    """Root endpoint providing API information"""
    return {
        "message": "Report Finding Refiner API",
        "version": "1.0.0",
        "model": DEFAULT_MODEL,
        "db_path": DEFAULT_DB_PATH,
        "reports_table": DEFAULT_TABLE_NAME,
        "endpoints": {
            "search": "/search",
            "reports": "/reports",
            "finding_models": "/findingmodel",
            "llm": "/llm"
        }
    }