# Search Service

The Search Service provides web search capabilities using DuckDuckGo when the knowledge base can't answer a query.

## Features

- Web search using DuckDuckGo
- Configurable search parameters
- Clean API for search requests and responses

## API Endpoints

### GET /

Returns basic information about the API.

### POST /search

Search the web using DuckDuckGo.

**Request Body:**
```json
{
  "query": "Your search query",
  "max_results": 5,
  "region": "wt-wt",
  "safesearch": "moderate",
  "timelimit": null
}
```

**Response:**
```json
{
  "results": [
    {
      "title": "Search result title",
      "href": "https://example.com/result",
      "body": "Search result snippet or description"
    }
  ]
}
```

## Configuration

The service doesn't require any specific environment variables, but you can configure the search parameters in the request.

## Running the Service

### Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn app:app --reload --port 8002
```

### With Docker

```bash
docker build -t search-service .
docker run -p 8002:8002 search-service
```

### With Docker Compose

```bash
docker-compose up search-service
```
