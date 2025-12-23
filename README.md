Contains helpers and tests for ingesting documents into S3 Vectors.

## Overview
- `ingest_from_file.py` — batch ingestion helper that reads a JSON array of documents and ingests them into S3 Vectors.
- `data/despicable_me_main_characters.json` — a short dataset of main characters (paraphrased) from the "Despicable Me" Wikipedia page; each entry includes `source` and `source_url` metadata. **Source:** Wikipedia (CC BY‑SA 4.0).


## Prerequisites 🔧
- Configure your project `.env` (project root) with at least:
  - `VECTOR_BUCKET` — your vector-enabled bucket name
  - `SAGEMAKER_ENDPOINT` — SageMaker inference endpoint name
  - `INDEX_NAME` — name of the S3 Vectors index (defaults to `despme-index`)
 
uv run ingest_from_file.py data/despicable_me_main_characters.json

python3 ingest_from_file.py data/despicable_me_main_characters.json
