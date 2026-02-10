# LLM Negotiation Arena

Multi-Agent Negotiation Simulation using Large Language Models

## Project Structure

```
nlp/
├── scenarios/          # JSON files for negotiation scenarios
├── personas/           # Persona definitions and management
├── agents/            # Agent classes and LLM integration
├── simulation/        # Negotiation engine and loop
├── analysis/          # Academic metrics and batch testing
├── utils/             # Helper functions (MongoDB, scenario loader)
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
- 🎭 **Diverse Personas**: 8 personalities (Aggressive, Fair, Liar, Logical, Cooperative, Stubborn, Desperate, Strategic)
- 📊 **Real-time Visualization**: Watch negotiations unfold live in the browser
- ⚖️ **Judge as Referee**: LLM checks for agreement after each round
- 💾 **MongoDB Integration**: All negotiations saved for analysis
- 📈 **Academic Metrics**: Agreement rate, rounds to convergence, utility scores, language complexity
- 🧪 **Batch Testing**: Run multiple negotiations automatically for statistical analysis
- 🔬 **Objective Analysis**: Mathematical calculations, not LLM opinions

## Status

✅ Step 1: Project Structure Setup - Complete  
✅ Step 2: Scenario System - Complete  
✅ Step 3: Persona System (Minimal, Emergent) - Complete  
✅ Step 4: Base Agent Class - Complete  
✅ Step 5: Negotiation Engine (Real-time Referee) - Complete  
✅ Step 6: Judge System (Factual Detection Only) - Complete  
✅ Step 7: Streamlit Website - Complete  
✅ Step 8: MongoDB Integration - Complete  
✅ Step 9: Academic Metrics Implementation - Complete  
✅ Step 10: Batch Testing System - Complete  
✅ Step 11: Language Complexity Analysis - Complete

## Academic Metrics

### Run Batch Testing:
```bash
python analysis/batch_testing.py
```

### Calculate Metrics:
```bash
python analysis/calculate_metrics.py
```

### Metrics Included:
- ✅ Agreement Rate (% successful negotiations)
- ✅ Rounds to Convergence (average rounds until agreement)
- ✅ Utility Scores (calculated from value functions)
- ✅ Language Complexity (word count, readability, vocabulary richness)
- ✅ Persona Comparisons (statistics by persona pairing)

**All metrics use standard academic methods, NOT LLM opinions!**

## Next Steps

- [ ] Statistical significance testing (t-tests, ANOVA)
- [ ] Data visualization (charts, graphs)
- [ ] Qualitative analysis (manual transcript review)
- [ ] Write report (abstract, methodology, results, discussion)
