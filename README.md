# Debate Chatbot API

A REST API for a chatbot that engages in debates, maintaining a specified stance and persuading the user.

## Setup
1. **Prerequisites**: Python 3.9+, Docker, Docker Compose.
2. Clone the repository: `git clone <repo-url> && cd chatbot-api`.
3. Copy `.env.example` to `.env` and set:
   - `OPENAI_API_KEY`: Your OpenAI API key (get from https://platform.openai.com).
4. **Install dependencies:**
   - **Unix/Linux/Mac**: `make install`
   - **Windows**: `cmd /c "run.bat install"` or `.\run.ps1 install`
5. **Start the service:**
   - **Unix/Linux/Mac**: `make run`
   - **Windows**: `cmd /c "run.bat run"` or `.\run.ps1 run`

## Environment Variables
- `OPENAI_API_KEY`: Required for OpenAI API access.

## API Usage
- **Endpoint**: `POST /debate`
- **Request**:
  ```json
  {
      "conversation_id": "abc123" | null,
      "message": "Debate that the Earth is flat, take the pro side"
  }
  ```
- **Response**:
  ```json
  {
      "conversation_id": "abc123",
      "message": [
          {"role": "user", "message": "Debate that the Earth is flat, take the pro side"},
          {"role": "bot", "message": "The Earth appears flat from our perspective..."}
      ]
  }
  ```

## Commands

**Unix/Linux/Mac (preferred):**
- `make`: List all commands
- `make install`: Install all requirements to run the service
- `make test`: Run tests
- `make run`: Run the service and all related services in Docker
- `make down`: Teardown of all running services
- `make clean`: Teardown and removal of all containers

**Windows PowerShell:**
- `.\run.ps1 help`: List all commands
- `.\run.ps1 install`: Install dependencies
- `.\run.ps1 test`: Run tests
- `.\run.ps1 run`: Start the service with Docker
- `.\run.ps1 down`: Stop all services
- `.\run.ps1 clean`: Remove all containers and images

**Windows Command Prompt:**
- `run.bat help`: List all commands
- `run.bat install`: Install dependencies
- `run.bat test`: Run tests
- `run.bat run`: Start the service with Docker
- `run.bat down`: Stop all services
- `run.bat clean`: Remove all containers and images

## Project Structure
```
chatbot-api/
├── src/
│   ├── __init__.py          # Makes src a Python package
│   ├── main.py              # FastAPI application with /debate endpoint
│   ├── models.py            # Pydantic models for request/response
│   ├── debate_service.py    # Logic for handling conversations and LLM calls
│   ├── storage.py           # SQLite database interactions
│   ├── prompts.py           # LangChain prompt templates
├── tests/
│   ├── __init__.py          # Makes tests a Python package
│   ├── test_api.py          # Tests for API endpoints
│   ├── test_debate.py       # Tests for debate logic
├── Dockerfile               # Docker configuration for the app
├── docker-compose.yml       # Docker Compose for running the app
├── Makefile                 # Build and run commands
├── README.md                # Instructions and env vars
└── requirements.txt         # Python dependencies
```

## Features
- **LangChain Integration**: Uses LangChain for prompt management and conversation flow
- **OpenAI GPT-4**: Powered by OpenAI's language models for persuasive responses
- **SQLite Storage**: Persistent conversation storage with topic and stance tracking
- **Topic Detection**: Automatically parses debate topics and stances from user messages
- **Conversation Memory**: Maintains context across multiple message exchanges
- **Docker Support**: Fully containerized with Docker Compose

## Example Workflow
- **New Conversation**:
  - Request: `POST /debate {"conversation_id": null, "message": "Debate that the Earth is flat, take the pro side"}`
  - API generates conversation_id, parses topic/stance, stores in SQLite, calls LLM
  - Returns: conversation_id and message history
- **Follow-Up**:
  - Request: `POST /debate {"conversation_id": "abc123", "message": "Photos show a round Earth"}`
  - API retrieves conversation, generates contextual response, updates SQLite
  - Returns: last 5 message pairs

## Notes
- Uses SQLite for simplicity; Redis or MongoDB recommended for production.
- Deployed to a public URL (e.g., Render) for testing.
- Tarball available via `git archive -o chatbot-api.tar.gz HEAD`.
