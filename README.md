# ReportFindingRefiner: Automated Clinical Findings Extraction from Radiology Reports

ReportFindingRefiner is a Python-based application that streamlines the process of mining radiology text reports for structured data models of clinical findings called FindingModels. It leverages local Large Language Model (LLM) engines (e.g., LLaMA) and vector embeddings to let users:
	1.	Upload a batch of radiology text reports (e.g., CT or MRI findings).
	2.	Ingest & Embed these reports into a local vector database (LanceDB).
	3.	Query these texts with a local LLM (such as Ollama’s LLaMA), extracting key clinical attributes—like pulmonary nodule descriptions or other relevant findings.
	4.	Generate structured outputs capturing the qualitative and quantitative attributes of the identified findings.

## Why This Project?
	•	No Technical Knowledge Needed: The tool aims to be incredibly easy to run from the command line, without requiring the user to manually install Python or manage Python dependencies.
	•	Automated LLM Setup: It simplifies spinning up an Ollama-based LLM so users don’t have to configure models manually.
	•	Local & Private: All data is processed locally; there’s no requirement to send protected health information (PHI) to remote servers, supporting HIPAA-compliant usage scenarios.

## Key Features
	1.	Automated Ingestion: Upload plain-text (.txt) radiology reports into a designated folder, run a single command, and let the system parse, embed, and store these reports in LanceDB.
	2.	Smart Searching: Perform textual, semantic, or hybrid searches to find relevant sections about specific conditions (e.g., nodules, masses, implants).
	3.	LLM Chat Extraction: Once retrieved, relevant text fragments are bundled into a prompt to a local LLM. You can ask questions like:
        •	“List all pulmonary nodules found and their approximate sizes.”
        •	“Identify any mention of hepatic steatosis or fatty liver.”
        •	“What are the typical attributes of a pulmonary nodule?”
	4.	Structured Attributes: The LLM can automatically parse out clinically meaningful data fields—dimensions, location, severity, etc.—to build a structured summary of the findings.

## How It Works
	1.	Vector Embeddings
        •	Each text segment is transformed into embedding vectors using a Hugging Face model.
        •	LanceDB stores these embeddings to enable efficient similarity or keyword-based retrieval.
	2.	Local LLM Query
        •	Through Ollama or a similar local LLM runner, your question and selected context are passed to a GPT-style model.
        •	The model generates natural language answers, highlighting relevant text or listing extracted attributes.
	3.	Zero-Fuss Installation
        •	The vision for this tool is to bundle all dependencies (Python environment, LanceDB, Ollama, etc.) so that end users only need to run a single installer.
        •	After installation, commands like report-refiner ingest or report-refiner query are available out of the box.

## Getting Started
	1.	Usage:
        •	Place .txt radiology reports in ./data/reports.
        •	Run report-refiner ingest to parse and store embeddings.
        •	Use report-refiner search --query "fatty liver" or report-refiner query --query "List all pulmonary nodules" to retrieve matched text or ask the LLM a question.
	2.	Development:
        •	For those who want to modify code, clone this repo and install locally with pip install . or pip install -e ..

### Contributing

Contributions for new extraction logic, advanced queries, or better local model support are welcome. See CONTRIBUTING.md for guidelines (planned).