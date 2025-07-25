# How to run TestGenie backend

## Prerequisites

Before running the TestGenie backend, ensure you have the following installed:

- **Python 3.8+**
- **Git**
- **Flutter SDK** (will be installed in SDKs directory)
- **MySQL Server**

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd f:\Thesis\Backend
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Required packages include:
- flask
- flask-cors
- langchain
- langchain-openai
- langchain-chroma
- langchain-community
- mysql-connector-python
- python-dotenv
- beautifulsoup4
- requests

### 3. Set up Environment Variables

Create a `.env` file in the Backend directory with the following configuration:

```env
# Database Configuration
DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=testgenie_db

# LLM Configuration (LM Studio or OpenAI-compatible API)
BASE_URL=http://localhost:1234/v1
BLA_LLM_MODEL=qwen2.5-7b-instruct
TG_LLM_MODEL=qwen2.5-7b-instruct
EMBED_MODEL=nomic-embed-text

# LangChain Configuration (optional)
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_PROJECT=TestGenie
```

### 4. Set up MySQL Database

1. Install and start MySQL server
2. Create a database named `testgenie_db` (or use the name specified in your `.env` file)
3. The application will automatically create the required tables on first run

```sql
CREATE DATABASE testgenie_db;
```

### 5. Install Flutter SDK

The system requires Flutter SDK to be installed in the `SDKs/flutter` directory:

1. Download Flutter SDK from https://flutter.dev/docs/get-started/install
2. Extract to `f:\Thesis\Backend\ProjectManager\SDKs\flutter`
3. Ensure the `flutter` command is accessible from `SDKs/flutter/bin/flutter`

### 6. Set up LM Studio (for local AI inference)

1. Download and install LM Studio from https://lmstudio.ai/
2. Download the Qwen2.5 7B Instruct 1M - Q4_K_M model
3. Load the model and start the local server on port 1234
4. Ensure the server is running before starting the backend

### 7. Add Documentation Files

Place Flutter documentation files in the following directories:
- `BusinessLogicAnalyzer/AI_Agent/docs/flutter_tutorial.pdf`
- `TestGenerator/docs/flutter_tutorial.pdf`

These files are used for Retrieval-Augmented Generation (RAG) to improve AI predictions.

## Running the Application

### Start the Flask Backend

```bash
cd f:\Thesis\Backend
python main.py
```

The backend will start on `http://localhost:5000` with the following endpoints:

- `POST /createProject` - Initialize a new project
- `POST /getDiagram` - Get project dependency diagram
- `POST /getBlockDetail` - Get detailed information about a code block
- `POST /updateBlockPrediction` - Update AI prediction for a block
- `POST /generateTest` - Generate test cases for a block

### Development Mode

For development with auto-reload:

```bash
flask --app main.py --debug run
```

## API Usage Examples

### Create Project
```bash
curl -X POST http://localhost:5000/createProject \
  -H "Content-Type: application/json" \
  -d '{"git_url": "https://github.com/username/flutter-project"}'
```

### Get Diagram
```bash
curl -X POST http://localhost:5000/getDiagram \
  -H "Content-Type: application/json" \
  -d '{"git_url": "https://github.com/username/flutter-project"}'
```

### Generate Test
```bash
curl -X POST http://localhost:5000/generateTest \
  -H "Content-Type: application/json" \
  -d '{"git_url": "https://github.com/username/flutter-project", "block_id": 123}'
```

## Directory Structure
