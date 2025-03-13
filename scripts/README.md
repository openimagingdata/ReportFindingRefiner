# Report Finding Refiner CLI Scripts

This directory contains command-line interface (CLI) scripts for the Report Finding Refiner application. These scripts provide convenient access to the core functionality of the application from the command line.

## Installation

The scripts are included as part of the Report Finding Refiner package. No additional installation is required beyond installing the main package.

## Usage

All scripts can be run using Python:

```bash
python scripts/script_name.py [arguments]
```

## Available Scripts

### 1. ingest.py

Ingests reports from a folder into the database.

#### Arguments

```
usage: ingest.py [-h] [--db-path DB_PATH] [--table-name TABLE_NAME] [--verbose] [--reports-folder REPORTS_FOLDER] [--force]

Ingest reports into the database

optional arguments:
  -h, --help            show this help message and exit
  --db-path DB_PATH     Path to the LanceDB database (default: /Users/yz/ReportFindingRefiner/data/lancedb/)
  --table-name TABLE_NAME
                        Name of the table in the database (default: table)
  --verbose, -v         Enable verbose output
  --reports-folder REPORTS_FOLDER
                        Path to the folder containing report files (default: /Users/yz/ReportFindingRefiner/data/reports_10/)
  --force, -f           Force re-creation of the database table
```

#### Examples

```bash
# Ingest reports from the default folder
python scripts/ingest.py

# Ingest reports from a custom folder with verbose output
python scripts/ingest.py --reports-folder ./data/custom_reports --verbose

# Force re-creation of the database table
python scripts/ingest.py --force
```

### 2. search.py

Searches for text in the reports database.

#### Arguments

```
usage: search.py [-h] [--db-path DB_PATH] [--table-name TABLE_NAME] [--verbose] [--mode {basic,vector,hybrid}] [--limit LIMIT] [--output {text,json}] [--full] [--compare] query

Search reports in the database

positional arguments:
  query                 The search query

optional arguments:
  -h, --help            show this help message and exit
  --db-path DB_PATH     Path to the LanceDB database (default: /Users/yz/ReportFindingRefiner/data/lancedb/)
  --table-name TABLE_NAME
                        Name of the table in the database (default: table)
  --verbose, -v         Enable verbose output
  --mode {basic,vector,hybrid}
                        Search mode to use (default: basic)
  --limit LIMIT         Maximum number of results to return (default: 10)
  --output {text,json}, -o {text,json}
                        Output format (default: text)
  --full, -f            Show full text in results (default: truncated)
  --compare             Compare search methods (basic, vector, hybrid)
```

#### Examples

```bash
# Basic search
python scripts/search.py "fatty liver"

# Vector-based semantic search with increased limit
python scripts/search.py "fatty liver" --mode vector --limit 20

# Compare different search methods
python scripts/search.py "fatty liver" --compare

# Get full results in JSON format
python scripts/search.py "fatty liver" --full --output json
```

### 3. findings.py

Manages finding models for radiology findings.

#### Subcommands

* `list`: List all finding models
* `view`: View a specific finding model
* `create`: Create a new finding model

#### Arguments for `list`

```
usage: findings.py list [-h] [--db-path DB_PATH] [--table-name TABLE_NAME] [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  --db-path DB_PATH     Path to the LanceDB database (default: /Users/yz/ReportFindingRefiner/data/lancedb/)
  --table-name TABLE_NAME
                        Name of the table in the database (default: table)
  --verbose, -v         Enable verbose output
```

#### Arguments for `view`

```
usage: findings.py view [-h] [--db-path DB_PATH] [--table-name TABLE_NAME] [--verbose] [--format {json,markdown}] name

positional arguments:
  name                  Name of the finding model to view

optional arguments:
  -h, --help            show this help message and exit
  --db-path DB_PATH     Path to the LanceDB database (default: /Users/yz/ReportFindingRefiner/data/lancedb/)
  --table-name TABLE_NAME
                        Name of the table in the database (default: table)
  --verbose, -v         Enable verbose output
  --format {json,markdown}
                        Output format (default: markdown)
```

#### Arguments for `create`

```
usage: findings.py create [-h] [--db-path DB_PATH] [--table-name TABLE_NAME] [--verbose] [--mode {basic,vector,hybrid}] [--limit LIMIT] [--description DESCRIPTION] [--synonyms SYNONYMS [SYNONYMS ...]] [--use-context] name

positional arguments:
  name                  Name of the finding

optional arguments:
  -h, --help            show this help message and exit
  --db-path DB_PATH     Path to the LanceDB database (default: /Users/yz/ReportFindingRefiner/data/lancedb/)
  --table-name TABLE_NAME
                        Name of the table in the database (default: table)
  --verbose, -v         Enable verbose output
  --mode {basic,vector,hybrid}
                        Search mode to use (default: basic)
  --limit LIMIT         Maximum number of results to return (default: 10)
  --description DESCRIPTION, -d DESCRIPTION
                        Description of the finding (if not provided, one will be generated)
  --synonyms SYNONYMS [SYNONYMS ...], -s SYNONYMS [SYNONYMS ...]
                        Synonyms for the finding name
  --use-context, -c     Use context from searching reports
```

#### Examples

```bash
# List all finding models
python scripts/findings.py list

# View a specific finding model
python scripts/findings.py view "Hepatic Steatosis" --format markdown

# Create a new finding model
python scripts/findings.py create "Pulmonary Nodule" --description "A small, round growth in the lung" --synonyms "lung nodule" "coin lesion"

# Create a model with context from existing reports
python scripts/findings.py create "Pulmonary Embolism" --use-context --mode vector
```

### 4. report.py

Manages and views reports in the database.

#### Subcommands

* `list`: List all reports
* `view`: View a specific report

#### Arguments for `list`

```
usage: report.py list [-h] [--db-path DB_PATH] [--table-name TABLE_NAME] [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  --db-path DB_PATH     Path to the LanceDB database (default: /Users/yz/ReportFindingRefiner/data/lancedb/)
  --table-name TABLE_NAME
                        Name of the table in the database (default: table)
  --verbose, -v         Enable verbose output
```

#### Arguments for `view`

```
usage: report.py view [-h] [--db-path DB_PATH] [--table-name TABLE_NAME] [--verbose] [--format {markdown,json}] report_id

positional arguments:
  report_id             ID of the report to view

optional arguments:
  -h, --help            show this help message and exit
  --db-path DB_PATH     Path to the LanceDB database (default: /Users/yz/ReportFindingRefiner/data/lancedb/)
  --table-name TABLE_NAME
                        Name of the table in the database (default: table)
  --verbose, -v         Enable verbose output
  --format {markdown,json}
                        Output format (default: markdown)
```

#### Examples

```bash
# List all reports
python scripts/report.py list

# View a specific report in markdown format
python scripts/report.py view "report1.txt"

# View a report in JSON format
python scripts/report.py view "report1.txt" --format json
```

## Common Options

All scripts support the following common options:

* `--db-path`: Path to the LanceDB database (default from config)
* `--table-name`: Name of the table in the database (default from config)
* `--verbose` or `-v`: Enable verbose output with detailed error messages

## Configuration

The scripts use default values from the application's configuration file. These defaults can be overridden using command-line arguments.

## Error Handling

All scripts include error handling with informative error messages. Use the `--verbose` flag to see detailed stack traces when errors occur.
