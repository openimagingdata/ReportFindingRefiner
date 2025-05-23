# ReportFindingRefiner
> Automated Clinical Findings Extraction from Radiology Reports

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

ReportFindingRefiner is a Python-based application that streamlines the process of mining radiology text reports for structured data models of clinical findings called FindingModels. It leverages local Large Language Model (LLM) engines (e.g., LLaMA via Ollama) and vector embeddings to enable:

1. **Batch Upload & Processing**: Upload radiology text reports (CT, MRI findings)
2. **Local Vector Database**: Ingest & embed reports into LanceDB for efficient retrieval
3. **LLM-Powered Querying**: Query texts with local LLMs, extracting key clinical attributes
4. **Structured Output Generation**: Generate FindingModels capturing qualitative and quantitative attributes

## 🎯 Why This Project?

* **Privacy-First**: All data processing happens locally—no PHI sent to remote servers, supporting HIPAA-compliant usage
* **No External Dependencies**: Uses local LLM infrastructure (Ollama) instead of cloud-based APIs
* **Automated Pipeline**: From raw text reports to structured clinical data models with minimal manual intervention
* **Research-Ready**: Built for medical research workflows requiring structured data extraction from unstructured reports

## ✨ Key Features

### 🔄 Automated Ingestion Pipeline
- Upload plain-text (.txt) radiology reports into designated folders
- Automatic text parsing, section splitting (Header, Findings, Impression)
- Vector embedding generation using Sentence Transformers
- Storage in LanceDB for efficient similarity search

### 🔍 Multi-Modal Search Capabilities
- **Basic Search**: Text-based keyword matching
- **Vector Search**: Semantic similarity using embeddings
- **Hybrid Search**: Combines both approaches for optimal results
- Search comparison tools for method evaluation

### 🤖 LLM-Powered Information Extraction
- Local LLM integration via Ollama (LLaMA, etc.)
- Context-aware querying with retrieved document fragments
- Structured finding model generation
- Template-based prompt engineering

### 📊 Clinical Finding Models
- Standardized data structures for clinical findings
- Automatic attribute extraction (dimensions, location, severity)
- MongoDB integration for finding model persistence
- Extensible schema for different finding types

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Text Reports  │───▶│  Section Split  │───▶│   Embeddings    │
│   (.txt files)  │    │   & Fragment    │    │  (Transformers) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────┐             ▼
                       │  Finding Models │    ┌─────────────────┐
                       │   (MongoDB)     │◀───│    LanceDB      │
                       └─────────────────┘    │  (Vector Store) │
                                 ▲            └─────────────────┘
                                 │                      │
                       ┌─────────────────┐             ▼
                       │  Local LLM      │    ┌─────────────────┐
                       │   (Ollama)      │◀───│ Search Service  │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.11 or higher
- **Ollama**: For local LLM serving ([Installation Guide](https://ollama.ai/))
- **MongoDB**: For finding model storage (optional)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/ReportFindingRefiner.git
   cd ReportFindingRefiner
   ```

2. **Install dependencies using uv** (recommended):
   ```bash
   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install project dependencies
   uv sync
   ```

   **Or using pip**:
   ```bash
   pip install -e .
   ```

3. **Set up Ollama and pull a model**:
   ```bash
   # Install Ollama (if not already done)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull LLaMA 3 model
   ./pull-llama3.sh
   # or manually: ollama pull llama3.2
   ```

4. **Create data directories**:
   ```bash
   mkdir -p data/reports data/lancedb
   ```

### Quick Start

1. **Place your radiology reports** in `./data/reports/` as `.txt` files

2. **Ingest reports into the vector database**:
   ```bash
   python scripts/ingest_reports.py
   ```

3. **Search for specific findings**:
   ```bash
   python scripts/search_reports.py --query "fatty liver" --mode hybrid
   ```

4. **Query with LLM for structured extraction**:
   ```bash
   python scripts/query_llm.py --query "List all pulmonary nodules and their attributes"
   ```

## 📖 Usage Examples

### Basic Search Operations

```bash
# Semantic search for liver findings
python scripts/search_reports.py --query "hepatic steatosis" --mode vector --limit 5

# Compare different search methods
python scripts/search_reports.py --query "lung nodules" --compare

# Keyword-based search
python scripts/search_reports.py --query "pulmonary" --mode basic
```

### LLM-Powered Queries

```bash
# Generate finding descriptions
python scripts/get_finding_description.py --finding_type "pulmonary_nodule"

# Extract structured finding information
python scripts/generate_finding_outline.py --finding_type "liver_lesion"

# Context-aware finding generation
python scripts/generate_finding_outline_with_context.py \
    --finding_type "lung_nodule" \
    --context_query "spiculated masses"
```

### Finding Model Management

```bash
# List all finding models in database
python scripts/list_finding_models.py

# Query specific finding types
python scripts/list_finding_models.py --finding_type "pulmonary_nodule"
```

## 🔧 Configuration

Key configuration options in `src/reportfindingrefiner/config.py`:

- **Database Paths**: LanceDB and MongoDB connection settings
- **Model Settings**: Embedding model and LLM configuration
- **Search Parameters**: Default search limits and modes

## 🐳 Docker Deployment

Build and run with Docker:

```bash
# Build the container
docker build -t reportfindingrefiner .

# Run with volume mounts for data persistence
docker run -v $(pwd)/data:/app/data reportfindingrefiner
```

## 🧪 Development

### Setting up Development Environment

```bash
# Clone and setup
git clone https://github.com/your-org/ReportFindingRefiner.git
cd ReportFindingRefiner

# Install in development mode
uv sync --dev

# Run tests
python -m pytest tests/
```

### Architecture Components

- **Data Models** (`data_models.py`): Pydantic models for type safety and validation
- **Services Layer**: 
  - `SearchService`: Handles all search operations (basic, vector, hybrid)
  - `ReportService`: Manages report ingestion and processing
  - `LLMService`: Centralizes LLM interactions
  - `FindingModelService`: Manages clinical finding data structures
- **Section Splitter**: Intelligent text parsing for medical report structure
- **Database Abstraction**: Clean interfaces for LanceDB and MongoDB


### Development Workflow

```bash
# Install development dependencies
uv sync --dev

# Run linting and formatting
ruff check --fix .
ruff format .

# Run tests
pytest tests/ -v

# Type checking
mypy src/
```

## 📋 Roadmap
This is very much a work in progress! Please reach out if you have any ideas or suggestions.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Built with ❤️ for the medical research community*