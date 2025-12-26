"""
Test script for the API Gateway ingestion endpoint.
Tests the full HTTP API pipeline with new Despicable Me content.
"""

import requests
import json
import time

# API Configuration
API_ENDPOINT = "https://your_endpoint.execute-api.us-east-1.amazonaws.com/prod/ingest"
API_KEY = "put your key here"

def test_api_ingestion(content, metadata=None):
    """Test ingesting content via API Gateway."""
    
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'text': content,  # Lambda expects 'text' field
        'metadata': metadata or {}
    }
    
    print(f"📤 Sending to API: {metadata.get('title', 'Unknown')}")
    print(f"   Content preview: {content[:100]}...")
    
    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=30)
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success! Document ID: {result.get('document_id', 'Unknown')}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ⏰ Timeout - Lambda may still be processing")
        return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    """Test API Gateway with new Despicable Me content."""
    
    print("🌐 API Gateway Ingestion Test")
    print("=" * 60)
    print(f"Endpoint: {API_ENDPOINT}")
    print(f"API Key: {API_KEY[:8]}...")
    print()
    
    # New test documents for API testing
    api_test_docs = [
        {
            'content': "Miss Hattie runs the Home for Girls where Margo, Edith, and Agnes live before being adopted by Gru. She's a stern woman who cares more about the adoption fees than the children's wellbeing. Miss Hattie is suspicious of Gru's intentions when he wants to adopt the girls for his scheme.",
            'metadata': {
                'title': 'Miss Hattie Profile',
                'character': 'Miss Hattie',
                'role': 'orphanage director',
                'movie': 'Despicable Me',
                'category': 'character',
                'source': 'api_test'
            }
        },
        {
            'content': "The Anti-Villain League (AVL) is a secret organization dedicated to fighting crime and tracking down supervillains. They recruit former villains like Gru to help with their missions. The AVL has advanced technology, underwater headquarters, and agents like Lucy Wilde who use specialized gadgets.",
            'metadata': {
                'title': 'Anti-Villain League Overview',
                'organization': 'AVL',
                'role': 'crime fighting agency',
                'movie': 'Despicable Me 2',
                'category': 'organization',
                'source': 'api_test'
            }
        },
        {
            'content': "Freedonia is the fictional country where Dru lives and maintains the family pig farm. It's a small European-style nation with rolling hills and traditional architecture. The country serves as a cover for the family's villainous activities, with secret underground lairs hidden beneath the pastoral landscape.",
            'metadata': {
                'title': 'Freedonia Country Profile',
                'location': 'Freedonia',
                'type': 'fictional country',
                'movie': 'Despicable Me 3',
                'category': 'location',
                'source': 'api_test'
            }
        },
        {
            'content': "The PX-41 serum is a dangerous mutagen that transforms any living creature into an indestructible purple monster. El Macho plans to use this serum on Minions to create an unstoppable army. The serum was stolen from a secret laboratory and represents one of the most dangerous weapons in the Despicable Me universe.",
            'metadata': {
                'title': 'PX-41 Serum Details',
                'item': 'PX-41 serum',
                'type': 'mutagen weapon',
                'movie': 'Despicable Me 2',
                'category': 'plot_device',
                'source': 'api_test'
            }
        },
        {
            'content': "Gru's house is shaped like a fortress with gray walls and a distinctive architectural style. Inside, it contains a secret laboratory, Minion living quarters, and various villainous gadgets. The house sits in a suburban neighborhood, making it an unusual sight among the typical family homes.",
            'metadata': {
                'title': 'Gru\'s House Description',
                'location': 'Gru\'s house',
                'type': 'villain lair',
                'movie': 'Despicable Me',
                'category': 'location',
                'source': 'api_test'
            }
        }
    ]
    
    print("Testing API Gateway ingestion with new content...")
    print()
    
    successful = 0
    total = len(api_test_docs)
    
    for i, doc in enumerate(api_test_docs, 1):
        print(f"{i}/{total}. Testing: {doc['metadata']['title']}")
        
        if test_api_ingestion(doc['content'], doc['metadata']):
            successful += 1
        
        print()
        
        # Small delay between requests to avoid rate limiting
        if i < total:
            time.sleep(1)
    
    print("=" * 60)
    print(f"📊 API Gateway Test Results:")
    print(f"   ✅ Successful: {successful}/{total}")
    print(f"   ❌ Failed: {total - successful}/{total}")
    
    if successful == total:
        print("\n🎉 All API tests passed! Your ingestion pipeline is working perfectly!")
        print("\n📚 New content added to knowledge base:")
        for doc in api_test_docs:
            print(f"   • {doc['metadata']['title']}")
        
        print("\n🔍 Try searching for:")
        print("   • 'orphanage director who cares about fees'")
        print("   • 'secret organization fighting crime'") 
        print("   • 'purple monster transformation serum'")
        print("   • 'fortress house in suburban neighborhood'")
        
    elif successful > 0:
        print(f"\n⚠️  Partial success - {successful} out of {total} documents ingested")
        print("   Check CloudWatch logs for any errors")
        
    else:
        print("\n❌ All API tests failed - check your configuration:")
        print("   • Is the Lambda function deployed correctly?")
        print("   • Are environment variables set properly?")
        print("   • Check CloudWatch logs for errors")

if __name__ == "__main__":
    main()
