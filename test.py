import chromadb
from pathlib import Path

client = chromadb.PersistentClient(path="./chroma_store")
col = client.get_collection("recipies_whole_doc")

# get all generated recipe IDs
results = col.get(where={"type": "generated"})
if results["ids"]:
    col.delete(ids=results["ids"])
    print(f"Deleted {len(results['ids'])} generated recipes")
    print(f"Remaining: {col.count()} vectors")