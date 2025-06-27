# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Lite Research is an AI-powered research tool built with Python that helps users conduct intelligent topic research and generate structured reports. It's a simplified version inspired by gpt-researcher, focusing on core functionality with cleaner architecture.

## Common Development Commands

### Running the Application
```bash
# Start the application
uv run run_app.py

# Or directly with Streamlit
uv run streamlit run frontend/literesearch_app.py
```

### Environment Setup
```bash
# Install dependencies (automatically managed by UV)
uv sync

# Copy environment template
cp env.example .env
# Then edit .env with your API keys
```

### Required Environment Variables
- `OPENAI_API_KEY_DEEPSEEK` or `OPENAI_API_KEY_SILICONCLOUD`: LLM API key
- `TAVILY_API_KEY`: Web search API key  
- `EMBEDDING_API_KEY`: Text embedding API key
- `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`: Optional monitoring

## Architecture Overview

### Core Components
- **Frontend**: Streamlit app (`frontend/literesearch_app.py`) - main UI and user interaction
- **Backend**: Research engine (`backend/literesearch/`) - AI research logic
- **Utils**: Shared utilities (`utils/`) - LLM tools and monitoring

### Key Modules
- `literesearcher.py`: Main research orchestrator class
- `literesearch_agent.py`: AI agent selection and query generation
- `web_retriever.py`: Web search and content extraction
- `embedding_service.py`: Vector similarity and content compression
- `llm_tools.py`: LLM provider abstraction (supports multiple APIs)

### Research Flow
1. User inputs research topic
2. System selects appropriate AI agent based on topic
3. Generates multiple sub-queries for comprehensive coverage
4. Parallel web search and content extraction
5. Vector-based content compression and relevance filtering
6. Structured report generation based on selected type/tone

### Configuration
- All settings centralized in `literesearch_config.py`
- Constants defined in `constants.py`
- Environment variables loaded via `utils/env_loader.py`
- SQLite caching enabled for LLM calls (`data/llm_cache/`)

## Development Notes

### UI Components
- Core app logic in `frontend/literesearch_app.py`
- UI styling and components in `frontend/ui_components.py`
- Clear separation between functionality and presentation

### LLM Integration
- Multi-provider support (DeepSeek, SiliconCloud, etc.)
- Langfuse monitoring integration (optional)
- Token limit management and temperature control
- Async processing for parallel operations

### Import Structure
The frontend uses relative imports with fallback to sys.path modification for flexibility in different execution contexts.