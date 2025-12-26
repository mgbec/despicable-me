"""
Search script for exploring the Despicable Me knowledge base.
Demonstrates semantic search capabilities with BGE-M3 embeddings.
"""

import os
import json
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from project root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path, override=True)

# Get configuration
VECTOR_BUCKET = os.getenv('VECTOR_BUCKET')
SAGEMAKER_ENDPOINT = os.getenv('SAGEMAKER_ENDPOINT', 'despme--embedding-endpoint')
INDEX_NAME = os.getenv('INDEX_NAME', 'despme-index')

if not VECTOR_BUCKET:
    print("Error: Please run Guide 3 Step 4 to save VECTOR_BUCKET to .env")
    exit(1)

# Initialize AWS clients
s3_vectors = boto3.client('s3vectors')
sagemaker_runtime = boto3.client('sagemaker-runtime')

def get_embedding(text):
    """Get embedding vector from SageMaker endpoint using BGE-M3."""
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT,
        ContentType='application/json',
        Body=json.dumps({'inputs': text})
    )
    
    result = json.loads(response['Body'].read().decode())
    # BGE-M3 returns nested array [[[embedding]]], extract the actual embedding
    if isinstance(result, list) and len(result) > 0:
        if isinstance(result[0], list) and len(result[0]) > 0:
            if isinstance(result[0][0], list):
                return result[0][0]  # Extract from [[[embedding]]]
            return result[0]  # Extract from [[embedding]]
    return result  # Return as-is if not nested

def search_vectors(query_text, k=5):
    """Search for vectors by query text."""
    print(f"\n🔍 Searching for: '{query_text}'")
    print("-" * 50)
    
    try:
        # Get embedding for query
        query_embedding = get_embedding(query_text)
        
        # Search S3 Vectors
        response = s3_vectors.query_vectors(
            vectorBucketName=VECTOR_BUCKET,
            indexName=INDEX_NAME,
            queryVector={"float32": query_embedding},
            topK=k,
            returnDistance=True,
            returnMetadata=True
        )
        
        vectors = response.get('vectors', [])
        print(f"Found {len(vectors)} results:\n")
        
        for i, vector in enumerate(vectors, 1):
            metadata = vector.get('metadata', {})
            distance = vector.get('distance', 0)
            similarity = 1 - distance  # Convert distance to similarity score
            
            print(f"{i}. 📊 Similarity: {similarity:.3f}")
            if metadata.get('title'):
                print(f"   📝 Title: {metadata['title']}")
            if metadata.get('character'):
                print(f"   👤 Character: {metadata['character']}")
            if metadata.get('movie'):
                print(f"   🎬 Movie: {metadata['movie']}")
            if metadata.get('category'):
                print(f"   📂 Category: {metadata['category']}")
            
            # Show text preview
            text = metadata.get('text', '')
            preview = text[:150] + '...' if len(text) > 150 else text
            print(f"   📖 Text: {preview}")
            print()
            
    except Exception as e:
        print(f"❌ Error searching: {e}")

def search_by_character(character_name, k=3):
    """Search for content about a specific character."""
    print(f"\n👤 Character Search: '{character_name}'")
    print("-" * 50)
    
    try:
        # Get embedding for character query
        query_embedding = get_embedding(f"{character_name} character profile personality")
        
        response = s3_vectors.query_vectors(
            vectorBucketName=VECTOR_BUCKET,
            indexName=INDEX_NAME,
            queryVector={"float32": query_embedding},
            topK=10,  # Get more results to filter
            returnDistance=True,
            returnMetadata=True
        )
        
        vectors = response.get('vectors', [])
        
        # Filter for exact character matches first
        character_lower = character_name.lower()
        exact_matches = [v for v in vectors if character_lower in v.get('metadata', {}).get('character', '').lower()]
        
        if exact_matches:
            print(f"Found {len(exact_matches)} documents about {character_name}:\n")
            for i, vector in enumerate(exact_matches[:k], 1):
                metadata = vector.get('metadata', {})
                similarity = 1 - vector.get('distance', 0)
                
                print(f"{i}. 📊 Similarity: {similarity:.3f}")
                print(f"   📝 {metadata.get('title', 'Unknown')}")
                print(f"   🎬 {metadata.get('movie', 'Unknown')}")
                print(f"   📖 {metadata.get('text', '')[:200]}...")
                print()
        else:
            print(f"No exact matches for '{character_name}'. Showing semantic results:\n")
            for i, vector in enumerate(vectors[:k], 1):
                metadata = vector.get('metadata', {})
                similarity = 1 - vector.get('distance', 0)
                print(f"{i}. 📊 Similarity: {similarity:.3f} - {metadata.get('character', 'Unknown')}")
                print(f"   📝 {metadata.get('title', 'Unknown')}")
                print()
                
    except Exception as e:
        print(f"❌ Error in character search: {e}")

def main():
    """Explore the Despicable Me knowledge base with various searches."""
    
    print("🍌 Despicable Me Knowledge Base Explorer 🍌")
    print("=" * 60)
    print(f"Bucket: {VECTOR_BUCKET}")
    print(f"Index: {INDEX_NAME}")
    print(f"Model: {SAGEMAKER_ENDPOINT} (BGE-M3)")
    print()
    
    # Semantic search examples
    print("🔍 SEMANTIC SEARCH EXAMPLES")
    print("=" * 60)
    
    search_queries = [
        "villain with orange tracksuit and bowl cut hair",
        "stealing the moon with shrink ray technology", 
        "yellow helpers who speak gibberish and love bananas",
        "three orphaned sisters adopted by supervillain",
        "1980s nostalgia disco dancing former child star",
        "secret agent with lipstick weapons"
    ]
    
    for query in search_queries:
        search_vectors(query, k=2)
    
    # Character-specific searches
    print("\n👤 CHARACTER-SPECIFIC SEARCHES")
    print("=" * 60)
    
    characters = ["Vector", "Gru", "Minions", "Lucy"]
    
    for character in characters:
        search_by_character(character, k=2)
    
    print("\n✨ SEMANTIC SEARCH MAGIC!")
    print("Notice how BGE-M3 finds relevant content even when:")
    print("• Query words don't exactly match document text")
    print("• Concepts are described differently")
    print("• Relationships and context matter more than keywords")
    print("\nThis is the power of semantic embeddings! 🚀")

if __name__ == "__main__":
    main()
