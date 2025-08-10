# Developer Documentation

## Text Analytics Endpoint

### `/analytics/text` (POST)

Invokes the local LLM (Ollama) for text analytics using either HTTP or CLI.

**Request Body:**
```json
{
  "text": "Analyze this text for sentiment.",
  "task": "summarization",
  "mode": "http" // "http" for HTTP API, "cli" for CLI invocation
}
```

- `text`: Input text for analysis (required)
- `task`: Task type (e.g., summarization, sentiment) (optional, default: "summarization")
- `mode`: `"http"` (default) uses Ollama HTTP API, `"cli"` uses Ollama CLI

**Response:**
```json
{
  "task": "summarization",
  "result": "...",
  "provider": "ollama",
  "endpoint": "http://localhost:11434/api/generate",
  "mode": "http"
}
```

**Swagger/OpenAPI:**
- The endpoint is documented with request/response models.
- The `mode` field allows switching between HTTP and CLI invocation.

**Notes:**
- Ensure Ollama is running locally for both HTTP and CLI modes.
- CLI mode requires the `ollama` binary in your system PATH.

Refer to other sections for authentication, database, and plugin endpoints.
