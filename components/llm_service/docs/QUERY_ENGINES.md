# Query Engines

Query Engines allow you to create searchable knowledge bases from various data sources. They support different types of data including text, images, video and audio.

## Types of Query Engines

There are three main types of query engines:

- **Vertex Search** (`qe_vertex_search`) - Uses Google Cloud Vertex AI Search for document indexing and retrieval
- **LLM Service** (`qe_llm_service`) - Uses the LLM Service's built-in vector store capabilities
- **Integrated Search** (`qe_integrated_search`) - Combines multiple query engines into a single interface

## Creating a Query Engine

Query engines can be created through either:

1. The web UI under the "Query Engines" page
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

### Document Sources

The following document source types are supported via the `doc_url` parameter:

- Google Cloud Storage: `gs://bucket/path`
- Web URLs: `http://` or `https://`
- BigQuery tables: `bq://project.dataset.table` 
- SharePoint: `shpt://site/path`

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
- The generated answer
- Source references with document URLs and relevant excerpts
- A unique query ID for retrieving the conversation history

## Managing Query Engines

### Listing Engines

Get all available query engines:

```bash
curl "https://{YOUR_DOMAIN}/llm-service/api/v1/query" \
  -H "Authorization: Bearer {TOKEN}"
```

### Getting Engine Details

Get details for a specific engine:

```bash
curl "https://{YOUR_DOMAIN}/llm-service/api/v1/query/engine/{ENGINE_ID}" \
  -H "Authorization: Bearer {TOKEN}"
```

### Updating an Engine

Update engine description:

```bash
curl -X PUT "https://{YOUR_DOMAIN}/llm-service/api/v1/query/engine/{ENGINE_ID}" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description"
  }'
```

### Deleting an Engine

Delete a query engine and all associated data:

```bash
curl -X DELETE "https://{YOUR_DOMAIN}/llm-service/api/v1/query/engine/{ENGINE_ID}" \
  -H "Authorization: Bearer {TOKEN}"
```

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

## Best Practices

1. **Document Organization**
   - Group related documents in the same source folder
   - Use consistent file formats within a query engine
   - Consider document size and chunking parameters

2. **Query Engine Design**
   - Create separate engines for different topics/domains
   - Use descriptive names and descriptions
   - Consider access patterns when choosing engine type

3. **Performance**
   - Monitor query response times
   - Adjust chunk sizes based on document types
   - Use appropriate embedding and vector store types

4. **Security**
   - Ensure proper access controls on document sources
   - Use non-public engines for sensitive data
   - Review and clean up unused engines 