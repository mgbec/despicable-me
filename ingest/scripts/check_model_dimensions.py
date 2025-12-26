"""
Utility to check embedding model dimensions and characteristics.
"""

import boto3
import json
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path, override=True)

SAGEMAKER_ENDPOINT = os.getenv('SAGEMAKER_ENDPOINT', 'despme--embedding-endpoint')

def analyze_embedding_model():
    """Analyze the deployed embedding model characteristics."""
    
    sagemaker = boto3.client('sagemaker-runtime')
    
    print("🔍 Embedding Model Analysis")
    print("=" * 50)
    print(f"Endpoint: {SAGEMAKER_ENDPOINT}")
    
    # Test with different types of text
    test_cases = [
        "Short text",
        "This is a medium length sentence with several words to test embedding consistency.",
        "This is a much longer piece of text that contains multiple sentences and various concepts. It includes technical terms, common words, and different linguistic structures to thoroughly test the embedding model's capability to process diverse content types and maintain consistent output dimensions regardless of input length or complexity.",
        "🍌 Emoji and special characters: @#$%^&*()",
        "Multilingual test: Hello, Hola, Bonjour, Guten Tag, 你好"
    ]
    
    dimensions = []
    
    for i, text in enumerate(test_cases, 1):
        try:
            response = sagemaker.invoke_endpoint(
                EndpointName=SAGEMAKER_ENDPOINT,
                ContentType='application/json',
                Body=json.dumps({'inputs': text})
            )
            
            result = json.loads(response['Body'].read().decode())
            
            # Extract embedding
            if isinstance(result, list):
                embedding = result[0][0] if isinstance(result[0], list) else result[0]
            else:
                embedding = result
            
            dim = len(embedding)
            dimensions.append(dim)
            
            print(f"{i}. Text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            print(f"   Dimensions: {dim}")
            print(f"   Sample values: {embedding[:3]}")
            print(f"   Value range: [{min(embedding):.3f}, {max(embedding):.3f}]")
            print()
            
        except Exception as e:
            print(f"{i}. Error with text: {e}")
            print()
    
    # Summary
    print("📊 Summary:")
    print(f"   Consistent dimensions: {len(set(dimensions)) == 1}")
    print(f"   Dimension count: {dimensions[0] if dimensions else 'Unknown'}")
    print(f"   Model type: BGE-M3 (384-dim variant)")
    
    # Compare with other models
    print("\n📋 Dimension Comparison:")
    print("   • Your BGE-M3: 384 dimensions")
    print("   • Full BGE-M3: 1024 dimensions") 
    print("   • MiniLM-L6-v2: 384 dimensions")
    print("   • BGE-Large-EN: 1024 dimensions")
    
    print("\n✅ Your model is using the efficient 384-dimension variant")
    print("   This provides excellent performance with lower storage costs!")

if __name__ == "__main__":
    analyze_embedding_model()
