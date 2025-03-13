# Services Layer

This directory contains the service classes that implement the core business logic of the Report Finding Refiner application. The service layer decouples the API and CLI interfaces from the underlying implementation.

## Service Classes

The application is divided into the following service classes:

- **SearchService**: Handles searching for text in report fragments
- **ReportService**: Manages report ingestion, retrieval, and formatting
- **LLMService**: Provides interaction with language models for generating content
- **FindingModelService**: Handles creation and management of finding models

## Design Principles

The service layer follows these design principles:

1. **Single Responsibility**: Each service focuses on a specific domain capability
2. **Interface Segregation**: Services expose clear, cohesive interfaces for their functionality
3. **Dependency Injection**: Services can be composed and dependencies injected for flexibility
4. **Reusability**: Services can be used by both API endpoints and CLI scripts

## Usage Examples

Services can be used in both API endpoints and CLI scripts:

```python
# In an API endpoint
from reportfindingrefiner.services import SearchService

search_service = SearchService()
results = search_service.search("query text", mode="hybrid")
return {"results": results}

# In a CLI script
from reportfindingrefiner.services import ReportService

report_service = ReportService()
report_service.ingest_reports("./data/reports")
```

## Benefits of the Service Layer

- **Consistency**: Same business logic used in both API and CLI
- **Testability**: Services can be unit tested independently of interfaces
- **Maintainability**: Changes to business logic only need to be made in one place
- **Flexibility**: New interfaces (e.g., GUI) can be added using the same services 