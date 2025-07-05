# AI FastAPI Server

A modular, OpenAI-compatible FastAPI server powered by GPT4Free (G4F) that provides access to multiple AI providers through a unified API interface.

## Features

- **OpenAI-Compatible API**: Full compatibility with OpenAI API v1 endpoints
- **Multiple AI Providers**: Access to various AI providers through G4F integration
- **Chat Completions**: Support for both streaming and non-streaming chat responses
- **Image Generation**: AI-powered image generation with multiple models
- **Modular Architecture**: Clean, maintainable code structure with separation of concerns
- **Rate Limiting**: Built-in request rate limiting and throttling
- **Request Logging**: Comprehensive logging and monitoring
- **Error Handling**: Robust error handling with detailed error responses
- **CORS Support**: Configurable Cross-Origin Resource Sharing
- **Health Monitoring**: Health check and status endpoints

## Project Structure

```
ai-fast-api/
├── app/
│   ├── __init__.py              # Package initialization with version info
│   ├── main.py                  # FastAPI application factory
│   ├── config.py                # Configuration management
│   ├── models.py                # Pydantic models for requests/responses
│   ├── api/
│   │   ├── __init__.py          # API routes package
│   │   ├── chat.py              # Chat completion endpoints
│   │   ├── images.py            # Image generation endpoints
│   │   ├── models.py            # Models and providers endpoints
│   │   └── health.py            # Health check endpoints
│   ├── services/
│   │   ├── __init__.py          # Services package
│   │   └── g4f_service.py       # G4F integration service
│   └── utils/
│       ├── __init__.py          # Utilities package
│       ├── logger.py            # Centralized logging
│       └── middleware.py        # Custom middleware
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Quick Start

### Prerequisites

- Python 3.9+
- `uv` package manager (recommended)

### Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd ai-fast-api
   ```

2. **Install dependencies using uv** (recommended):

   ```bash
   python install_dependencies.py

```

This script uses `uv` to install dependencies from `requirements.txt`. If `uv` is not installed, the script will provide instructions on how to install it.

   Or using pip:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

### Run the Application

To run the FastAPI application in development mode (activates virtual environment and starts the server):

```bash
python dev_start.py
```

Alternatively, you can run it directly with Uvicorn (ensure your virtual environment is activated):

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation

Once the server is running, you can access:

- **API Documentation**: <http://localhost:8000/docs>
- **ReDoc Documentation**: <http://localhost:8000/redoc>
- **Health Check**: <http://localhost:8000/health>

## Usage Examples

### Using curl

#### List Available Models

```bash
curl -X GET "http://localhost:8000/v1/models" \
  -H "Authorization: Bearer sk-test-key-123"
```

#### Chat Completion (Non-streaming)

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-test-key-123" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {
        "role": "user",
        "content": "Hello, how are you?"
      }
    ],
    "temperature": 0.7,
    "max_tokens": 150
  }'
```

#### Chat Completion (Streaming)

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-test-key-123" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {
        "role": "user",
        "content": "Write a short poem about technology"
      }
    ],
    "stream": true
  }'
```

### Using Python with OpenAI Library

```python
from openai import OpenAI

# Initialize client with your local server
client = OpenAI(
    api_key="sk-test-key-123",
    base_url="http://localhost:8000/v1"
)

# Create a chat completion
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Explain quantum computing in simple terms"}
    ],
    temperature=0.7,
    max_tokens=200
)

print(response.choices[0].message.content)
```

### Using Python with Streaming

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-test-key-123",
    base_url="http://localhost:8000/v1"
)

# Create a streaming chat completion
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Tell me a story about AI"}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
```

## Available Models

- `gpt-4o-mini` (default)
- `gpt-4o`
- `gpt-4`
- `gpt-3.5-turbo`
- `claude-3-sonnet`
- `gemini-pro`

## Configuration

### Configuration

Configuration is managed via environment variables. A `.env.example` file is provided to help you set up. Copy this file to `.env` and modify the values as needed.

Key variables include:

- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)
- `DEBUG`: Enable debug mode (default: `false`)
- `G4F_PROVIDER`: Default G4F provider (default: `auto`)
- `G4F_MODEL`: Default G4F model (default: `gpt-3.5-turbo`)
- `G4F_TIMEOUT`: G4F request timeout in seconds (default: `60`)
- `G4F_RETRIES`: Number of G4F request retries (default: `3`)
- `RATE_LIMIT_REQUESTS`: Max requests per minute for rate limiting (default: `60`)
- `RATE_LIMIT_WINDOW`: Rate limit window in seconds (default: `60`)
- `CORS_ENABLED`: Enable CORS (default: `true`)
- `CORS_ORIGINS`: Comma-separated list of allowed CORS origins (default: `*`)
- `OPENAI_API_BASE`: Base path for OpenAI compatible API (default: `/v1`)

These can be set directly in your environment or by creating a `.env` file in the project root.

### API Keys

By default, the following API keys are configured for testing:

- `sk-test-key-123` (test environment)
- `secret` (development)
- Custom key from `API_KEY` environment variable

**⚠️ Important**: In production, replace these with secure, randomly generated API keys.

## API Endpoints

### Chat Completions

**POST** `/v1/chat/completions`

Create a chat completion with support for streaming and non-streaming responses.

**Request Body**:

```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "user",
      "content": "Hello!"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 150,
  "stream": false
}
```

### Models

**GET** `/v1/models`

List all available models.

### Health Check

**GET** `/health`

Check server health status.

## Error Handling

The API includes comprehensive error handling:

- **401 Unauthorized**: Invalid or missing API key
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server or AI service errors

Errors are returned in OpenAI-compatible format:

```json
{
  "error": {
    "message": "Invalid API key",
    "type": "invalid_request_error",
    "code": 401
  }
}
```

## Rate Limiting

The server implements rate limiting to prevent abuse:

- Default: 10 requests per second per client
- Configurable via environment variables
- Uses token bucket algorithm with `aiolimiter`

## Retry Logic

Built-in retry mechanism for handling transient errors:

- Maximum 3 retry attempts
- Exponential backoff (4-10 seconds)
- Automatic retry on network/service errors

## Development

### Project Structure

```
ai-fast-api/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── .env                # Environment configuration
├── README.md           # This file
└── .gitignore         # Git ignore rules
```

### Running in Development Mode

```bash
# With auto-reload
python main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Testing

Test the API endpoints:

```bash
# Health check
curl http://localhost:8000/health

# List models
curl -H "Authorization: Bearer sk-test-key-123" http://localhost:8000/v1/models

# Chat completion
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-test-key-123" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Hello!"}]}'
```

## Deployment

### Using Docker (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations

1. **Security**:
   - Use strong, unique API keys
   - Enable HTTPS/TLS
   - Implement proper authentication
   - Set up firewall rules

2. **Performance**:
   - Use multiple workers: `uvicorn main:app --workers 4`
   - Configure appropriate rate limits
   - Monitor resource usage

3. **Monitoring**:
   - Set up logging aggregation
   - Monitor API response times
   - Track error rates
   - Monitor G4F service availability

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure all dependencies are installed

   ```bash
   uv pip install -r requirements.txt
   ```

2. **G4F Connection Issues**: Check internet connection and G4F service status

3. **Rate Limiting**: Adjust `MAX_REQUESTS_PER_SECOND` in `.env`

4. **Authentication Errors**: Verify API key in request headers

### Logs

Check server logs for detailed error information:

```bash
# Run with debug logging
LOG_LEVEL=debug python main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Acknowledgments

- [GPT4Free (G4F)](https://github.com/xtekky/gpt4free) for providing free AI model access
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [OpenAI](https://openai.com/) for the API specification
