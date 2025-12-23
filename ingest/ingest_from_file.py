"""
Batch ingestion helper for S3 Vectors.

Usage:
  # Ensure your .env has VECTOR_BUCKET, SAGEMAKER_ENDPOINT and INDEX_NAME
  cd backend/ingest
  uv run ingest_from_file.py data/sample_docs.json

Or directly:
  python3 ingest_from_file.py data/sample_docs.json

The script reads a JSON array of {"text": ..., "metadata": {...}} and ingests each document.
"""

import json
import os
import sys
import time
import uuid
from pathlib import Path
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
import datetime

# Load .env from project root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path, override=True)

VECTOR_BUCKET = os.getenv('VECTOR_BUCKET')
SAGEMAKER_ENDPOINT = os.getenv('SAGEMAKER_ENDPOINT')
INDEX_NAME = os.getenv('INDEX_NAME', 'despme-index')

if not VECTOR_BUCKET or not SAGEMAKER_ENDPOINT:
    print("Error: Please set VECTOR_BUCKET and SAGEMAKER_ENDPOINT in your .env before running this script.")
    sys.exit(1)

sagemaker_runtime = boto3.client('sagemaker-runtime')
s3_vectors = boto3.client('s3vectors')


def get_embedding(text, attempts=3, delay=1):
    for attempt in range(attempts):
        try:
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=SAGEMAKER_ENDPOINT,
                ContentType='application/json',
                Body=json.dumps({'inputs': text})
            )
            result = json.loads(response['Body'].read().decode())
            # unpack nested HF output
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], list) and len(result[0]) > 0:
                    if isinstance(result[0][0], list):
                        return result[0][0]
                    return result[0]
            return result
        except ClientError as e:
            print(f"SageMaker ClientError: {e}")
            if attempt < attempts - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise
        except Exception as e:
            print(f"Unexpected SageMaker error: {e}")
            raise


def put_vector(vector_id, embedding, metadata, attempts=3, delay=1):
    for attempt in range(attempts):
        try:
            s3_vectors.put_vectors(
                vectorBucketName=VECTOR_BUCKET,
                indexName=INDEX_NAME,
                vectors=[{
                    "key": vector_id,
                    "data": {"float32": embedding},
                    "metadata": metadata
                }]
            )
            return
        except ClientError as e:
            code = e.response.get('Error', {}).get('Code')
            print(f"S3Vectors ClientError: {code} - {e}")
            if code == 'NotFoundException':
                raise RuntimeError(f"Index '{INDEX_NAME}' not found in bucket '{VECTOR_BUCKET}'")
            if attempt < attempts - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise


def ingest_docs(docs_path):
    with open(docs_path, 'r') as f:
        docs = json.load(f)

    print(f"Ingesting {len(docs)} documents from {docs_path}")
    successes = 0
    failures = 0

    for i, doc in enumerate(docs, 1):
        text = doc.get('text')
        metadata = doc.get('metadata', {})
        print(f"[{i}/{len(docs)}] Getting embedding for text (len={len(text or '')})...")
        try:
            embedding = get_embedding(text)
            if not isinstance(embedding, list) or len(embedding) == 0:
                print("  ✗ Invalid embedding returned; skipping")
                failures += 1
                continue

            vector_id = str(uuid.uuid4())
            # add timestamp
            metadata = {**metadata, 'timestamp': datetime.datetime.utcnow().isoformat()}
            put_vector(vector_id, embedding, metadata)
            print(f"  ✓ Ingested as {vector_id}")
            successes += 1
        except Exception as e:
            print(f"  ✗ Failed to ingest document: {e}")
            failures += 1

    print(f"Finished: {successes} succeeded, {failures} failed")


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'data/sample_docs.json'
    ingest_docs(path)
