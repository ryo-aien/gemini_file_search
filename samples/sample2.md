# Getting Started with Gemini File Search

## Introduction

Gemini's File Search is a hosted question-answering service that makes it easy to build RAG systems using Google's infrastructure.

## Core Concepts

### File Search Stores

A **File Search Store** is a container for your documents. Think of it as a database or collection where you organize related documents.

### Documents

Documents are the individual files you upload to a store. Each document can have:
- Custom metadata (up to 20 key-value pairs)
- Configurable chunking settings
- MIME type specification

### Chunking

Documents are automatically split into chunks for embedding. You can configure:
- `max_tokens_per_chunk`: Maximum tokens per chunk (default: 200)
- `max_overlap_tokens`: Overlap between chunks (default: 20)

## Supported File Types

- Plain text (.txt)
- Markdown (.md)
- PDF documents (.pdf)
- HTML files (.html)
- CSV files (.csv)
- JSON files (.json)
- Microsoft Word (.doc, .docx)

## Best Practices

1. **Organize by topic**: Create separate stores for different content domains
2. **Use metadata**: Add metadata to enable filtering and better search results
3. **Optimize chunk size**: Adjust chunking based on your document structure
4. **Monitor storage**: Keep individual stores under 20 GB for optimal performance

## Example Use Case

Imagine building a customer support chatbot. You could:
1. Create a store for product documentation
2. Upload manuals, FAQs, and troubleshooting guides
3. Tag documents with product categories as metadata
4. Use the search API to find relevant information for customer queries

## Rate Limits

- **Free tier**: 1 GB storage
- **Pro tier**: 100 GB storage
- **Tier 3**: 1 TB storage

The API handles embedding and indexing automatically, with charges at $0.15 per million tokens for indexing.
