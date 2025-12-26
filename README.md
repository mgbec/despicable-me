# 🍌 Despicable Me Semantic Search Pipeline (DESPME)

A production-ready AI-powered semantic search system built on AWS, featuring BGE-M3 embeddings and S3 Vectors for cost-effective vector storage. This project demonstrates enterprise-grade document ingestion and semantic search capabilities using the Despicable Me universe as a knowledge base.

## 🎯 Project Overview

**DESPME** is a serverless semantic search pipeline that:
- Ingests documents via HTTP API
- Generates embeddings using state-of-the-art BGE-M3 model
- Stores vectors in cost-optimized S3 Vectors (90% cheaper than alternatives)
- Provides semantic search with natural language queries
- Implements enterprise-grade security and monitoring

## 🏗️ Architecture

```
📱 Client → 🌐 API Gateway → ⚡ Lambda → 🧠 SageMaker (BGE-M3) → 💾 S3 Vectors
                    ↓
               🔍 Semantic Search Results
```

### Core Components

- **API Gateway**: HTTP endpoint with API key authentication and rate limiting
- **Lambda Function**: Document processing and orchestration (Python 3.12)
- **SageMaker Endpoint**: BGE-M3 model for generating 384-dimensional embeddings
- **S3 Vectors**: Cost-effective vector database for semantic search
- **IAM Roles**: Multi-layered security with least privilege access

## 🚀 Features

### ✅ **Semantic Search Capabilities**
- Natural language queries: *"villain with orange tracksuit"* → Vector Perkins
- Conceptual matching: *"yellow helpers who love bananas"* → Minions
- Multi-language support: 100+ languages via BGE-M3
- High accuracy similarity scores (0.6-0.9 for relevant matches)

### ✅ **Production-Ready Infrastructure**
- **Serverless**: Pay-per-use, auto-scaling from 0 to peak demand
- **Cost-Optimized**: S3 Vectors provides 90% cost savings vs alternatives
- **Secure**: Multi-layered security with IAM roles and API authentication
- **Monitored**: Comprehensive logging and audit trails

### ✅ **Developer Experience**
- **Infrastructure as Code**: Complete Terraform deployment
- **Testing Suite**: Comprehensive test scripts for all components
- **Documentation**: Detailed setup guides and API documentation
- **Observability**: CloudWatch logging and performance monitoring

## 📊 Current Knowledge Base

The system contains **15 documents** about the Despicable Me universe:

**Characters**: Gru, Vector Perkins, Minions, Dr. Nefario, Lucy Wilde, El Macho, Balthazar Bratt, Dru, Miss Hattie

**Organizations**: Anti-Villain League (AVL)

**Locations**: Freedonia, Gru's house

**Plot Elements**: Moon heist, PX-41 serum, villain schemes

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Embeddings** | BGE-M3 (384-dim) | State-of-the-art multilingual embeddings |
| **Vector DB** | S3 Vectors | Cost-effective vector storage and search |
| **Compute** | AWS Lambda | Serverless document processing |
| **API** | API Gateway | HTTP endpoint with authentication |
| **Infrastructure** | Terraform | Infrastructure as Code |
| **Runtime** | Python 3.12 | Lambda function runtime |
| **Security** | IAM Roles | Multi-layered access control |

```

## 🚀 Quick Start

### Prerequisites

- AWS CLI configured with appropriate permissions
- Terraform >= 1.5
- Python 3.12 with uv package manager
- Docker Desktop (for Lambda packaging)

### 1. Deploy SageMaker Embedding Model

# Edit terraform.tfvars with your AWS region
terraform init
terraform apply
```
### Test the Pipeline

cd bngest
uv run test_despicable_me_docs.py    # Ingest sample documents
uv run search_despicable_me.py       # Test semantic search
uv run test_api_gateway.py           # Test HTTP API


## 🔍 Usage Examples

### Document Ingestion (HTTP API)

```bash
curl -X POST https://your-api-gateway-url/prod/ingest \
  -H "x-api-key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Vector Perkins is a supervillain who wears an orange tracksuit...",
    "metadata": {
      "character": "Vector",
      "movie": "Despicable Me",
      "category": "character"
    }
  }'
```

### Semantic Search (Python)

```python
from search_despicable_me import search_vectors

# Natural language queries
search_vectors("villain with orange tracksuit", k=3)
search_vectors("stealing the moon with shrink ray", k=3)
search_vectors("yellow helpers who speak gibberish", k=3)
```

### Sample Search Results

**Query**: `"villain with orange tracksuit"`
```
1. 📊 Similarity: 0.735
   📝 Title: Vector Perkins Profile
   👤 Character: Vector
   🎬 Movie: Despicable Me
   📖 Text: Vector Perkins is Gru's rival and nemesis, a young supervillain who wears an orange tracksuit...
```

## 📈 Performance Metrics

### Speed
- **Embedding Generation**: 200-500ms (serverless cold start)
- **Vector Storage**: 100-200ms
- **Search Query**: 100-300ms
- **Total Ingestion**: 1-2 seconds

### Accuracy
- **Semantic Understanding**: Excellent (BGE-M3)
- **Similarity Scores**: 0.6-0.9 for relevant matches
- **Multi-language**: 100+ languages supported
- **Context Awareness**: High conceptual matching

### Cost (Estimated for 10K operations/month)
- **SageMaker Serverless**: ~$2.00
- **S3 Vectors**: ~$0.02
- **Lambda**: ~$2.00
- **API Gateway**: ~$0.035
- **Total**: ~$4-6/month

## 🔐 Security Features

### Multi-Layered Security
- **API Gateway**: API key authentication, rate limiting, usage quotas
- **IAM Roles**: Least privilege access, service-bound roles
- **Data Protection**: AES256 encryption at rest, HTTPS in transit
- **Network Security**: Private S3 bucket, no public access
- **Audit Trail**: Comprehensive CloudWatch logging

### Security Controls
- ✅ Zero public data exposure
- ✅ Principle of least privilege
- ✅ Encrypted data at rest and in transit
- ✅ Rate limiting and DDoS protection
- ✅ Comprehensive audit logging
- ✅ Service isolation and contained blast radius

## 🧪 Testing

### Test Scripts Available

```bash
# Model and infrastructure tests
uv run check_model_dimensions.py     # Verify BGE-M3 model characteristics
uv run test_despicable_me_docs.py    # Ingest sample Despicable Me content
uv run search_despicable_me.py       # Test semantic search capabilities
uv run test_api_gateway.py           # Test HTTP API endpoint


### Sample Test Queries

- `"villain with orange tracksuit and bowl cut hair"` → Vector Perkins
- `"stealing the moon with shrink ray technology"` → Moon heist plot
- `"yellow helpers who speak gibberish and love bananas"` → Minions
- `"secret agent with lipstick weapons"` → Lucy Wilde
- `"1980s nostalgia disco dancing former child star"` → Balthazar Bratt

## 📚 Documentation

- **[Pipeline Workflow](pipeline_workflow.md)**: Detailed system architecture and data flow
- **[Security Analysis](security_analysis.md)**: Comprehensive security architecture review

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# AWS Configuration
AWS_REGION=us-east-1
DEFAULT_AWS_REGION=us-east-1

# SageMaker
SAGEMAKER_ENDPOINT=despme--embedding-endpoint

# S3 Vectors
VECTOR_BUCKET=my-despicable-bucket12212025
INDEX_NAME=despme-index

# API Gateway
DESPME_API_ENDPOINT=https://your-api-gateway-url/prod/ingest
DESPME_API_KEY=your-api-key-here
```

## 🚧 Future Enhancements

### Planned Features
- [ ] Web-based search interface
- [ ] Batch document ingestion
- [ ] Advanced filtering and faceted search
- [ ] Multi-modal search (text + images)
- [ ] Real-time analytics dashboard

### Infrastructure Improvements
- [ ] VPC deployment for enhanced network isolation
- [ ] AWS WAF for additional API protection
- [ ] Multi-region deployment for global availability
- [ ] Enhanced monitoring with custom CloudWatch dashboards


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **BGE-M3 Model**: Beijing Academy of Artificial Intelligence
- **AWS S3 Vectors**: Cost-effective vector database solution
- **Despicable Me Universe**: Universal Pictures and Illumination Entertainment
- **Course Inspiration**: "Generative and Agentic AI in Production" by Ed Donner https://www.udemy.com/course/generative-and-agentic-ai-in-production
