"""
Lambda function for searching S3 Vectors.
"""

import json
import os
import time
import boto3
from botocore.exceptions import ClientError

# Environment variables
VECTOR_BUCKET = os.environ.get('VECTOR_BUCKET', 'my-despicable-bucket12212025')
SAGEMAKER_ENDPOINT = os.environ.get('SAGEMAKER_ENDPOINT')
INDEX_NAME = os.environ.get('INDEX_NAME', 'despme-index')

# Validate environment variables at startup (fail early with clear message)
if not SAGEMAKER_ENDPOINT:
    raise RuntimeError("SAGEMAKER_ENDPOINT is not set; set it in Lambda env or .env")
if not VECTOR_BUCKET:
    raise RuntimeError("VECTOR_BUCKET is not set; set it in Lambda env or .env")
if not INDEX_NAME:
    raise RuntimeError("INDEX_NAME is not set; set it in Lambda env or .env")

# Initialize AWS clients
sagemaker_runtime = boto3.client('sagemaker-runtime')
s3_vectors = boto3.client('s3vectors')


def get_embedding(text):
    """Get embedding vector from SageMaker endpoint with retries and error handling."""
    attempts = 3
    delay = 1
    for attempt in range(attempts):
        try:
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=SAGEMAKER_ENDPOINT,
                ContentType='application/json',
                Body=json.dumps({'inputs': text})
            )

            result = json.loads(response['Body'].read().decode())
            # HuggingFace returns nested array [[[embedding]]], extract the actual embedding
            embedding = None
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], list) and len(result[0]) > 0:
                    if isinstance(result[0][0], list):
                        embedding = result[0][0]  # Extract from [[[embedding]]]
                    else:
                        embedding = result[0]  # Extract from [[embedding]]
            else:
                embedding = result  # Return as-is if not nested

            return embedding

        except ClientError as e:
            code = e.response.get('Error', {}).get('Code')
            print(f"ClientError calling SageMaker invoke_endpoint: {code} - {e}")
            # Retry on transient errors
            if attempt < attempts - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise
        except Exception as e:
            print(f"Unexpected error calling SageMaker: {e}")
            raise


def lambda_handler(event, context):
    """
    Search handler.
    Expects JSON body with:
    {
        "query": "Search query text",
        "k": 5  # Optional, defaults to 5
    }
    """
    # Parse the request body
    if isinstance(event.get('body'), str):
        body = json.loads(event['body'])
    else:
        body = event.get('body', {})
    
    query_text = body.get('query')
    k = body.get('k', 5)
    
    if not query_text:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required field: query'})
        }
    
    # Get embedding for query
    print(f"Getting embedding for query: {query_text}")
    query_embedding = get_embedding(query_text)

    # Validate k (must be int between 1 and 50)
    try:
        k = int(k)
    except Exception:
        k = 5
    if k <= 0:
        k = 5
    if k > 50:
        k = 50

    # Validate embedding
    if not isinstance(query_embedding, list) or len(query_embedding) == 0:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Invalid embedding returned from SageMaker'})
        }

    # Search S3 Vectors
    print(f"Searching in bucket: {VECTOR_BUCKET}, index: {INDEX_NAME}")
    try:
        response = s3_vectors.query_vectors(
            vectorBucketName=VECTOR_BUCKET,
            indexName=INDEX_NAME,
            queryVector={"float32": query_embedding},
            topK=k,
            returnDistance=True,
            returnMetadata=True
        )
    except ClientError as e:
        code = e.response.get('Error', {}).get('Code')
        print(f"ClientError querying vectors: {code} - {e}")
        if code == 'NotFoundException':
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f"Index '{INDEX_NAME}' not found in bucket '{VECTOR_BUCKET}'"})
            }
        if code in ('AccessDeniedException', 'AccessDenied'):
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Access denied. Ensure IAM role has s3vectors:* permissions'})
            }
        raise
    
    # Format results
    results = []
    for vector in response.get('vectors', []):
        results.append({
            'id': vector['key'],
            'score': vector.get('distance', 0),
            'text': vector.get('metadata', {}).get('text', ''),
            'metadata': vector.get('metadata', {})
        })
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'results': results,
            'count': len(results)
        })
    }
