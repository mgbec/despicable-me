"""
Lambda function for ingesting text into S3 Vectors with embeddings.
"""

import json
import os
import time
import boto3
from botocore.exceptions import ClientError
import datetime
import uuid

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
    Main Lambda handler.
    Expects JSON body with:
    {
        "text": "Text to ingest",
        "metadata": {
            "source": "optional source",
            "category": "optional category"
        }
    }
    """
    try:
        # Parse the request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        text = body.get('text')
        metadata = body.get('metadata', {})
        
        if not text:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required field: text'})
            }
        
        # Get embedding from SageMaker
        print(f"Getting embedding for text: {text[:100]}...")
        embedding = get_embedding(text)

        # Validate embedding
        if not isinstance(embedding, list) or len(embedding) == 0:
            print("Invalid embedding returned from SageMaker")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Invalid embedding returned from SageMaker'})
            }

        # Generate unique ID for the vector
        vector_id = str(uuid.uuid4())

        # Store in S3 Vectors with retries and error handling
        print(f"Storing vector in bucket: {VECTOR_BUCKET}, index: {INDEX_NAME}")
        attempts = 3
        delay = 1
        for attempt in range(attempts):
            try:
                s3_vectors.put_vectors(
                    vectorBucketName=VECTOR_BUCKET,
                    indexName=INDEX_NAME,
                    vectors=[{
                        "key": vector_id,
                        "data": {"float32": embedding},
                        "metadata": {
                            "text": text,
                            "timestamp": datetime.datetime.utcnow().isoformat(),
                            **metadata  # Include any additional metadata
                        }
                    }]
                )
                break
            except ClientError as e:
                code = e.response.get('Error', {}).get('Code')
                print(f"ClientError putting vectors: {code} - {e}")
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
                if attempt < attempts - 1:
                    time.sleep(delay)
                    delay *= 2
                    continue
                raise
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Document indexed successfully',
                'document_id': vector_id
            })
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

