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

### 3. Configure API Keys and Database

1. Copy the template file:
   ```bash
   cp env.template .env
   ```

2. Edit `.env` and add your credentials:
   - `OPENAI_API_KEY` (if using OpenAI)
   - `ANTHROPIC_API_KEY` (if using Anthropic)
   - `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_HOST` (MongoDB credentials)

3. Test MongoDB connection (optional):
   ```bash
   python test_mongodb.py
   ```

### 4. Run the Application

```bash
streamlit run app.py
```

## Features

- 🤖 **Multi-Agent Negotiation**: LLM-powered agents with distinct personalities
- 🎭 **Diverse Personas**: Aggressive, Fair, Liar, Logical, Cooperative, and more
- 📊 **Real-time Visualization**: Watch negotiations unfold live in the browser
- ⚖️ **Judge Analysis**: AI-powered evaluation of negotiation outcomes
- 💾 **MongoDB Integration**: All negotiations saved for analysis and research
- 📈 **Statistics Dashboard**: Track success rates, average rounds, and more

## Status

✅ Step 1: Project Structure Setup - Complete  
✅ Step 2: Scenario System - Complete  
✅ Step 3: Persona System - Complete  
✅ Step 4: Base Agent Class - Complete  
✅ Step 5: Negotiation Engine - Complete  
✅ Step 6: Judge/Adjudicator System - Complete  
✅ Step 7: Streamlit Website - Configuration Page - Complete  
✅ Step 8: Streamlit Website - Simulation Viewer - Complete  
✅ Step 9: MongoDB Integration - Complete

## Next Steps

- [ ] Step 10: Batch Testing System
- [ ] Step 11: Data Analysis and Export Tools
- [ ] Step 12: Report Generation
