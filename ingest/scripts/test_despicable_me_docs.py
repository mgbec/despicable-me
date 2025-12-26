"""
Test script for ingesting Despicable Me movie content to S3 Vectors.
This creates a knowledge base about the Despicable Me universe!
"""

import os
import json
import boto3
import uuid
import datetime
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

def ingest_document(text, metadata=None):
    """Ingest a document directly to S3 Vectors."""
    # Get embedding from SageMaker
    print(f"Getting embedding for: {metadata.get('title', 'Unknown')}...")
    embedding = get_embedding(text)
    
    # Generate unique ID for the vector
    vector_id = str(uuid.uuid4())
    
    # Store in S3 Vectors
    s3_vectors.put_vectors(
        vectorBucketName=VECTOR_BUCKET,
        indexName=INDEX_NAME,
        vectors=[{
            "key": vector_id,
            "data": {"float32": embedding},
            "metadata": {
                "text": text,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                **(metadata or {})  # Include any additional metadata
            }
        }]
    )
    
    return vector_id

def main():
    """Test ingestion with Despicable Me content."""
    
    print("🍌 Despicable Me Knowledge Base Creator 🍌")
    print("=" * 60)
    print(f"Bucket: {VECTOR_BUCKET}")
    print(f"Index: {INDEX_NAME}")
    print(f"Embedding Model: {SAGEMAKER_ENDPOINT} (BGE-M3)")
    print()
    
    # Despicable Me universe documents
    despicable_me_docs = [
        {
            'text': "Gru is a supervillain who lives in a house shaped like a fortress with his army of yellow Minions. He plans elaborate heists and schemes, including his most ambitious plot to steal the Moon using a shrink ray. Despite his villainous exterior, Gru has a soft heart and becomes a loving father to three orphaned girls: Margo, Edith, and Agnes.",
            'metadata': {
                'character': 'Gru',
                'role': 'protagonist/former villain',
                'movie': 'Despicable Me',
                'title': 'Gru Character Profile',
                'category': 'character'
            }
        },
        {
            'text': "Vector Perkins is Gru's rival and nemesis, a young supervillain who wears an orange tracksuit and has a bowl cut hairstyle. He lives on a fortress-like house and uses advanced technology including piranha guns and squid launchers. Vector successfully steals the Great Pyramid of Giza before Gru can, making him Gru's main competition in the villain world.",
            'metadata': {
                'character': 'Vector',
                'role': 'antagonist/villain',
                'movie': 'Despicable Me',
                'title': 'Vector Perkins Profile',
                'category': 'character'
            }
        },
        {
            'text': "The Minions are small, yellow, cylindrical creatures who serve as Gru's loyal helpers. They speak in a gibberish language called Minionese, which includes words from various languages. Minions love bananas, are naturally drawn to serving the most despicable master they can find, and often cause chaos with their well-meaning but clumsy attempts to help.",
            'metadata': {
                'character': 'Minions',
                'role': 'supporting characters',
                'movie': 'Despicable Me franchise',
                'title': 'Minions Overview',
                'category': 'character'
            }
        },
        {
            'text': "Dr. Nefario is Gru's elderly scientist and inventor who creates gadgets and weapons for Gru's villainous schemes. He has a German accent, wears thick glasses, and is hard of hearing, often mishearing Gru's instructions. Despite his age, he's brilliant at creating freeze rays, shrink rays, and other scientific marvels that aid in Gru's heists.",
            'metadata': {
                'character': 'Dr. Nefario',
                'role': 'supporting character/scientist',
                'movie': 'Despicable Me',
                'title': 'Dr. Nefario Profile',
                'category': 'character'
            }
        },
        {
            'text': "Gru's plan to steal the Moon involves using a shrink ray to make the Moon small enough to grab. He needs to obtain the shrink ray from Vector first, which leads to a series of elaborate schemes. The Moon heist represents the ultimate villainous achievement, something no supervillain has ever attempted before.",
            'metadata': {
                'plot': 'Moon heist',
                'movie': 'Despicable Me',
                'title': 'The Moon Stealing Plot',
                'category': 'plot'
            }
        },
        {
            'text': "Margo, Edith, and Agnes are three orphaned sisters who live at Miss Hattie's Home for Girls. Margo is the responsible eldest sister, Edith is the mischievous middle child who loves destruction, and Agnes is the youngest who adores unicorns and fluffy things. They become central to Gru's character development when he adopts them as part of his scheme but grows to genuinely love them.",
            'metadata': {
                'character': 'Margo, Edith, Agnes',
                'role': 'Gru\'s adopted daughters',
                'movie': 'Despicable Me',
                'title': 'The Three Girls',
                'category': 'character'
            }
        },
        {
            'text': "El Macho, whose real name is Eduardo Perez, is a legendary supervillain who was thought to be dead after riding a shark into an active volcano while strapped to dynamite. He now runs a Mexican restaurant called Salsa & Salsa in the mall. El Macho plans to use the PX-41 serum to create an army of indestructible Minions to take over the world.",
            'metadata': {
                'character': 'El Macho/Eduardo',
                'role': 'villain',
                'movie': 'Despicable Me 2',
                'title': 'El Macho Profile',
                'category': 'character'
            }
        },
        {
            'text': "Lucy Wilde is an agent of the Anti-Villain League (AVL) who recruits Gru to help track down a dangerous villain. She's energetic, optimistic, and skilled in combat, using lipstick tasers and other spy gadgets. Lucy eventually becomes Gru's love interest and later his wife, helping him transition from villain to hero while maintaining her own career as a secret agent.",
            'metadata': {
                'character': 'Lucy Wilde',
                'role': 'AVL agent/Gru\'s wife',
                'movie': 'Despicable Me 2',
                'title': 'Lucy Wilde Profile',
                'category': 'character'
            }
        },
        {
            'text': "Balthazar Bratt is a former child star from the 1980s who became a supervillain after his TV show was cancelled. He's obsessed with 80s culture, using disco music, dance fighting, and retro technology in his evil schemes. Bratt plans to destroy Hollywood as revenge for ending his career, using a giant robot and bubble gum to achieve his goals.",
            'metadata': {
                'character': 'Balthazar Bratt',
                'role': 'villain',
                'movie': 'Despicable Me 3',
                'title': 'Balthazar Bratt Profile',
                'category': 'character'
            }
        },
        {
            'text': "Dru is Gru's long-lost twin brother who lives in the country of Freedonia. Unlike Gru, Dru has a full head of blonde hair and maintains the family tradition of villainy. He owns a pig farm as a cover for his villainous activities and tries to convince Gru to return to his evil ways for one last heist together.",
            'metadata': {
                'character': 'Dru',
                'role': 'Gru\'s twin brother',
                'movie': 'Despicable Me 3',
                'title': 'Dru Profile',
                'category': 'character'
            }
        }
    ]
    
    # Ingest each document
    print("Ingesting Despicable Me documents...")
    print()
    
    for i, doc in enumerate(despicable_me_docs, 1):
        print(f"{i:2d}. {doc['metadata']['title']}")
        try:
            doc_id = ingest_document(doc['text'], doc['metadata'])
            print(f"     ✓ Success! ID: {doc_id[:8]}...")
        except Exception as e:
            print(f"     ✗ Error: {e}")
        print()
    
    print("🎉 Despicable Me Knowledge Base Created!")
    print("\nYour S3 Vectors database now contains:")
    print("📚 Characters: Gru, Vector, Minions, Dr. Nefario, Lucy, El Macho, Bratt, Dru")
    print("🎬 Movies: Despicable Me 1, 2, and 3")
    print("📖 Plots: Moon heist, family dynamics, villain schemes")
    
    print("\n🔍 Ready for semantic search! Try queries like:")
    print("   • 'villain with orange tracksuit'")
    print("   • 'stealing the moon'") 
    print("   • 'yellow helpers who love bananas'")
    print("   • 'three orphaned sisters'")
    print("   • '1980s nostalgia and disco'")
    
    print("\n⏱️  S3 Vectors updates are available immediately.")
    print("   Run the search test next to explore your knowledge base!")

if __name__ == "__main__":
    main()
