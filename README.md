# Day 5 - Serving Models Your Way

Scenario: College Study Assistant

## Files

- `Modelfile` - custom Ollama model configuration
- `ollama_rest.py` - REST API test with streaming and non-streaming requests
- `openai_compatible.py` - OpenAI-compatible endpoint test
- `analysis.md` - conceptual analysis and observation tables
- `requirements.txt` - Python packages
- `screenshots/` - add required screenshots after running the commands

## Create the model

```powershell
ollama create study-assistant -f Modelfile
ollama list
ollama show study-assistant
```

## Install Python packages

```powershell
pip install -r requirements.txt
```

## Run the REST API test

```powershell
python ollama_rest.py
```

## Run the OpenAI-compatible test

```powershell
python openai_compatible.py
```

## Check loaded models

```powershell
ollama ps
```

The real performance numbers and observations must be collected by running the project on the local machine.
