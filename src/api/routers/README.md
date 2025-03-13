# API Routers

This directory contains FastAPI router modules that organize the API endpoints by functionality.

## Router Structure

The API is divided into the following routers:

- **search_router.py**: Endpoints for searching reports
- **report_router.py**: Endpoints for managing reports and report ingestion
- **finding_model_router.py**: Endpoints for creating and managing finding models
- **llm_router.py**: Endpoints for direct LLM interaction

## Using Routers

Each router:

1. Initializes a FastAPI APIRouter object
2. Creates instances of the services it needs
3. Defines a set of endpoints related to its functionality
4. Handles request/response models and input validation

## How These Routers Work With Services

The routers act as a thin controller layer:
- They parse HTTP requests and validate inputs
- They call service layer methods from `src/reportfindingrefiner/services/*`
- They handle exceptions and format responses
- They do NOT contain business logic

This design allows:
- Clear separation of API routing concerns from business logic
- Better testability of both API endpoints and service logic
- Easier maintenance when API or business requirements change
- Reuse of business logic in both CLI and API contexts 