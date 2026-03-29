## Project Skills and Dependencies

This document lists the main tools, libraries, and platform components required for the AI-Powered Trip Planner Assistant.

## Step-by-Step Installation

Follow these steps to prepare the local development environment.

### 1. Create or Activate a Virtual Environment

If the virtual environment does not exist:

```powershell
python -m venv venv
```

Activate it in PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### 3. Install Core Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Install Ollama

Install Ollama from the official website if it is not already installed.

After installation, pull the recommended local model:

```powershell
ollama pull llama3.2
```

### 5. Verify Key Packages

```powershell
pip show streamlit crewai langchain langchain-community langchain-ollama duckduckgo-search
```

### 6. Run the Streamlit App

Once the application code is created, run it with:

```powershell
streamlit run app.py
```

### Notes

1. `pysqlite3-binary` is usually not required on Windows because Python already includes SQLite support.
2. Ollama must be installed separately because it is not a Python package.
3. Llama 3.2 should be downloaded locally through Ollama before running agents that depend on it.

### Core Application Framework

1. Streamlit
	Used to build the web-based user interface.

### Multi-Agent Orchestration

2. CrewAI
	Used to create and manage the multi-agent workflow.

3. `crewai[tools]`
	Used to enable CrewAI tool integrations for agent capabilities.

### Database and Local Storage

4. `pysqlite3-binary`
	Used for SQLite support in environments where binary packaging is required.

### LLM and Agent Integration

5. LangChain
	Used to support language model integration and workflow composition.

6. `langchain-community`
	Used for community-provided LangChain integrations and utilities.

7. `langchain-ollama`
	Used to connect LangChain with locally hosted Ollama models.

### Search and External Information Retrieval

8. `duckduckgo-search`
	Used to search the web for destination research and supporting travel information.

### Local Model Runtime

9. Ollama
	Used to run local language models for agent reasoning and content generation.

10. Llama 3.2
	 Suggested local model for use with Ollama.

### Recommended Use in This Project

The project should use:

1. Streamlit for the frontend
2. CrewAI for agent orchestration
3. LangChain and Ollama for model connectivity
4. DuckDuckGo Search for online research support
5. SQLite-based storage where lightweight local persistence is needed



