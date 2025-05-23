import lancedb
from reportfindingrefiner.search import search_in_db
from reportfindingrefiner.ingestion import read_reports_from_folder, ingest_reports

#ingest_reports("./data/reports", "./data/lancedb_search_test", "reports")
print("Searching for 'fatty liver' in vector mode...")
results = search_in_db("./data/lancedb_search_test", "reports", "fatty liver", "vector")
print("Results:")
# print the results without the vector field
for r in results:
    # Create a new dict excluding the vector field
    result_without_vector = {k: v for k, v in r.items() if k != 'vector'}
    print(result_without_vector)

