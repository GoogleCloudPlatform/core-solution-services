# Query Engines

Query Engines allow you to create searchable knowledge bases from various data sources. They support different types of data including text from both html and pdf documents and images. Video and audio are not yet supported but will be added soon.

## Types of Query Engines

There are three main types of query engines:

- **Vertex Search** (`qe_vertex_search`) - Uses Google Cloud Vertex AI Search for document indexing and retrieval
- **LLM Service** (`qe_llm_service`) - Uses the LLM Service's built-in vector store capabilities
- **Integrated Search** (`qe_integrated_search`) - Combines multiple query engines into a single interface

## Creating a Query Engine

Query engines can be created through either:

1. The web UI under the "Query Engines" page in the React frontend.
2. The REST API directly

### Using the REST API

To create a query engine via the API:

```bash
curl -X POST "https://{YOUR_DOMAIN}/llm-service/api/v1/query/engine" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "query_engine": "my-engine",
    "query_engine_type": "qe_vertex_search",
    "doc_url": "gs://my-bucket/docs",
    "embedding_type": "vertex_embedding",
    "vector_store": "vertex",
    "description": "My search engine",
    "params": {
      "chunk_size": 500
    }
  }'
```

Required fields:
- `query_engine` - Unique name for the engine (alphanumeric, dashes and spaces allowed)
- `query_engine_type` - One of: `qe_vertex_search`, `qe_llm_service`, `qe_integrated_search`
- `doc_url` - URL to the document source (GCS bucket, web URL, BigQuery table, or SharePoint site)
- `embedding_type` - Type of embeddings to use
- `description` - Description of the query engine

Optional fields:
- `vector_store` - Vector store to use (defaults to system default)
- `params` - Additional parameters like chunk size, depth limit, etc.
- `llm_type` - LLM to use for queries
- `manifest_url` - URL to a manifest file for additional configuration

### Query Engine Parameters

The `params` field accepts the following configuration options:

#### Document Processing
- `chunk_size` (int, default: 500)
  - Number of characters per text chunk when processing documents
  - Larger chunks provide more context but may reduce relevance accuracy
  - Smaller chunks increase build time significantly

- `depth_limit` (int, default: 0)
  - Controls web crawling depth when processing web URLs
  - Only applies when using web URLs as document sources
  - Values:
    - `0`: Download only the specified URL, don't follow any links
    - `1`: Download the specified URL and follow all links from that page
    - `2`: Download the specified URL, follow all links, and follow links from those pages
    - etc.
  - Higher values will increase processing time and storage requirements
  - Use caution with depth > 2 as the number of pages grows exponentially

- `is_multimodal` (bool, default: false)
  - Enable multimodal processing for images and text
  - When true, uses multimodal embedding models and LLMs

#### Access Control
- `is_public` (bool, default: true)
  - Controls visibility of the query engine
  - When false, only the creator can access the engine

#### Integration Options
- `agents` (list[str], optional)
  - List of agent IDs to enable for this engine. 

- `associated_engines` (list[str], optional)
  - List of query engine IDs to include in an integrated search
  - Only applies when `query_engine_type` is `qe_integrated_search`
  - Child engines must exist before creating the integrated engine

#### Vector Store Configuration
- `similarity_threshold` (float, default: 0.7)
  - Minimum similarity score (0.0 to 1.0) for including results
  - Higher values return only more relevant matches
  - Lower values return more results but may be less relevant
  - Recommended range: 0.5-0.9

- `max_results` (int, default: 10) 
  - Maximum number of similar chunks to retrieve per query
  - Higher values provide more context but increase response time
  - Lower values are faster but may miss relevant content
  - Recommended range: 5-20

### Document Sources

The following document source types are supported via the `doc_url` parameter:

- Google Cloud Storage: `gs://bucket/path`
- Web URLs: `http://` or `https://` (Only GENIE engines)
- BigQuery tables: `bq://project.dataset.table` (Only Vertex Search engines)
- SharePoint: `shpt://site/path` (Only GENIE engines)

The URL should point to a folder/container of documents, not individual files.

## Querying an Engine

Once created, you can query an engine via:

```bash
curl -X POST "https://{YOUR_DOMAIN}/llm-service/api/v1/query/engine/{ENGINE_ID}" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the capital of France?",
    "llm_type": "vertex"
  }'
```

The response will include:
```json
{
  "success": true,
  "message": "Successfully performed query",
  "data": {
    "query_id": "abc123",
    "query_engine_id": "my-engine",
    "query_engine": "my-engine",
    "prompt": "What is the capital of France?",
    "response": "The capital of France is Paris.",
    "references": [
      {
        "id": "ref123",
        "query_engine_id": "my-engine", 
        "query_engine": "my-engine",
        "document_id": "doc123",
        "document_url": "gs://my-bucket/docs/france.pdf",
        "modality": "text",
        "page": 1,
        "document_text": "Paris is the capital and largest city of France...",
        "chunk_id": "chunk123"
      }
    ],
    "history": [
      {
        "HumanQuestion": "What is the capital of France?"
      },
      {
        "AIResponse": "The capital of France is Paris."
      },
      {
        "AIReferences": [
          {
            "id": "ref123",
            "document_url": "gs://my-bucket/docs/france.pdf",
            "document_text": "Paris is the capital and largest city of France..."
          }
        ]
      }
    ]
  }
}
```

The response contains:
- `query_id` - Unique identifier for this query
- `query_engine_id` - ID of the query engine used
- `query_engine` - Name of the query engine used
- `prompt` - Original query prompt
- `response` - Generated answer from the LLM
- `references` - List of source references used to generate the answer, including:
  - Document URLs
  - Page numbers (for PDFs)
  - Relevant text excerpts
  - Timestamps (for audio/video)
- `history` - Conversation history including:
  - Human questions
  - AI responses 
  - Source references

## Query Engines API

See the API docs at `/llm-service/api/v1/docs` for details on building and managing query engines via the REST API. These docs are auto-generated from the FastAPI endpoints.

## Data Model

Query engines use several collections in Firestore to store their data:

- `query_engines` - Core engine configuration and metadata
- `query_documents` - Documents indexed by the engine
- `query_document_chunks` - Individual chunks/segments of documents
- `query_references` - References to source documents for answers
- `user_queries` - User query history and conversations

### Query Engine Model

The main query engine model contains:

```python
class QueryEngine:
    id: str                     # Unique ID
    name: str                   # Engine name
    query_engine_type: str      # Engine type
    description: str            # Description
    embedding_type: str         # Embedding type
    vector_store: str          # Vector store type
    doc_url: str               # Document source URL
    created_by: str            # Creator user ID
    is_public: bool            # Public visibility
    params: dict               # Additional parameters
```

### Query Document Model

Represents an indexed document:

```python
class QueryDocument:
    id: str                    # Unique ID  
    query_engine_id: str       # Parent engine ID
    doc_url: str               # Document URL
    index_file: str           # Index file name
    index_start: int          # Starting index
    index_end: int            # Ending index
    metadata: dict            # Document metadata
```

### Query Document Chunk Model

Represents a segment of an indexed document:

```python
class QueryDocumentChunk:
    id: str                    # Unique ID
    query_engine_id: str       # Parent engine ID
    query_document_id: str     # Parent document ID
    index: int                # Chunk index
    modality: str             # Content type
    text: str                 # Text content
    page: int                 # Page number
    chunk_url: str            # Media chunk URL
    timestamp_start: int      # Media start time
    timestamp_stop: int       # Media end time
```

