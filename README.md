# ReportFindingRefiner
> Automated Clinical Findings Extraction from Radiology Reports

ReportFindingRefiner is a Python-based application that streamlines the process of mining radiology text reports for structured data models of clinical findings called FindingModels. It leverages local Large Language Model (LLM) engines (e.g., LLaMA) and vector embeddings to let users:

1. Upload a batch of radiology text reports (e.g., CT or MRI findings)
2. Ingest & Embed these reports into a local vector database (LanceDB)
3. Query these texts with a local LLM (such as Ollama's LLaMA), extracting key clinical attributes
4. Generate structured outputs capturing the qualitative and quantitative attributes of the identified findings

## 🎯 Why This Project?

* **No Technical Knowledge Needed**: Easy to run from the command line, without requiring manual Python installation or dependency management
* **Automated LLM Setup**: Simplifies spinning up an Ollama-based LLM without manual configuration
* **Local & Private**: All data is processed locally—no PHI sent to remote servers, supporting HIPAA-compliant usage

## ✨ Key Features

### 1. Automated Ingestion
Upload plain-text (.txt) radiology reports into a designated folder, run a single command, and let the system parse, embed, and store these reports in LanceDB.

### 2. Smart Searching
Perform textual, semantic, or hybrid searches to find relevant sections about specific conditions (e.g., nodules, masses, implants).

### 3. LLM Chat Extraction
Once retrieved, relevant text fragments are bundled into a prompt to a local LLM. Example queries:

* "List all pulmonary nodules found and their approximate sizes"
* "Identify any mention of hepatic steatosis or fatty liver"
* "What are the typical attributes of a pulmonary nodule?"

### 4. Structured Attributes
The LLM automatically parses out clinically meaningful data fields—dimensions, location, severity, etc.—to build a structured summary of findings.

## 🔧 How It Works

### 1. Vector Embeddings
* Each text segment is transformed into embedding vectors using a Hugging Face model
* LanceDB stores these embeddings to enable efficient similarity or keyword-based retrieval

### 2. Local LLM Query
* Through Ollama or a similar local LLM runner, your question and selected context are passed to a GPT-style model
* The model generates natural language answers, highlighting relevant text or listing extracted attributes

### 3. Zero-Fuss Installation
* All dependencies (Python environment, LanceDB, Ollama, etc.) are bundled for simple installation
* After installation, commands like `report-refiner ingest` or `report-refiner query` are available out of the box

## 🚀 Getting Started

### Usage
1. Place `.txt` radiology reports in `./data/reports`
2. Run `report-refiner ingest` to parse and store embeddings
3. Use commands to interact with the data:
   ```bash
   report-refiner search --query "fatty liver"
   # or
   report-refiner query --query "List all pulmonary nodules and tell me about their attributes"
   ```