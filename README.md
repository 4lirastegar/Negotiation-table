# LLM Negotiation Arena

Multi-Agent Negotiation Simulation using Large Language Models

## Project Structure

```
nlp/
├── scenarios/          # JSON files for negotiation scenarios
├── personas/           # Persona definitions and management
├── agents/            # Agent classes and LLM integration
├── simulation/        # Negotiation engine and loop
├── testing/           # Batch testing scripts
├── utils/             # Helper functions
├── config/            # Configuration files
├── app.py             # Streamlit website (main entry)
└── requirements.txt   # Python dependencies
```

## Setup

### 1. Virtual Environment

To activate the virtual environment:

```bash
source venv/bin/activate
```

To deactivate:

```bash
deactivate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

1. Copy the template file:
   ```bash
   cp env.template .env
   ```

2. Edit `.env` and add your API keys:
   - `OPENAI_API_KEY` (if using OpenAI)
   - `ANTHROPIC_API_KEY` (if using Anthropic)

### 4. Run the Application

```bash
streamlit run app.py
```

## Status

✅ Step 1: Project Structure Setup - Complete  
✅ Step 2: Scenario System - Complete  
✅ Step 3: Persona System - Complete  
✅ Step 4: Base Agent Class - Complete  
✅ Step 5: Negotiation Engine - Complete  
✅ Step 6: Judge/Adjudicator System - Complete
