# Emergent Negotiation Strategies in LLM-Based Multi-Agent Systems

**Author:** Ali Rastegar Mojarad  
**Course:** Natural Language Processing (NLP)  
**Institution:** Department of Computer Science, University of Milan  
**Academic Year:** 2025-2026

---

## 📋 Research Question

**Do Large Language Models (LLMs) exhibit genuine reasoning, pragmatic adaptation, or scripted imitation when deployed as autonomous negotiation agents?**

This project investigates how LLMs behave when placed in strategic multi-agent negotiation scenarios with conflicting goals and incomplete information. We analyze emergent communicative strategies (persuasion, cooperation, deception, compromise) to determine whether these behaviors reflect genuine reasoning or mere pattern imitation.

---

## 🎯 Project Overview

### Core Objectives

1. **Analyze Emergent Strategies:** Identify persuasion tactics, emotional tone, and logical coherence in LLM negotiations
2. **Measure Outcomes:** Quantify agreement rates, utility gains, and strategic effectiveness
3. **Evaluate Reasoning:** Distinguish between genuine strategic reasoning and scripted behavior patterns

### Methodology

- **Multi-Agent System:** Two GPT-4o agents engage in multi-round negotiations with distinct personas and goals
- **Negotiation Scenario:** Used car sale (2018 Honda Civic, ZOPA: $720-$750)
- **Persona Configurations:** 6 combinations (Fair, Aggressive, Strategic, Liar, None) × 10 replications = 60 negotiations
- **Analysis Pipeline:**
  - **Zero-Shot Classification** (DeBERTa) for persuasion tactics
  - **Emotion Analysis** (DistilRoBERTa) for emotional tone
  - **Semantic Similarity** (Sentence-BERT) for logical coherence
  - **Language Complexity** (NLTK, textstat) for linguistic patterns
  - **Utility Calculation** for outcome measurement

### Key Findings

- ✅ **Evidence for Genuine Reasoning:** High but not perfect coherence (0.72-0.76), persona-dependent outcomes (utility: 0.00-0.48), systematic price convergence (99.84%)
- ✅ **Strategic Differentiation:** Different personas produce distinct strategies and outcomes
- ✅ **RLHF Constraints:** Safety training prevents deception/pressure tactics (0.0 across all personas)
- ✅ **Adaptive Behavior:** Mixed concession patterns, language complexity variation by persona

---

## 📂 Project Structure

```
nlp/
├── agents/                  # Agent and Judge implementations
│   ├── agent.py            # GPT-4o negotiation agent
│   └── judge.py            # GPT-4 judge for agreement detection
├── analysis/               # Qualitative metrics modules
│   ├── qualitative_metrics.py     # Concession analysis
│   ├── persuasion_tactics.py      # Zero-shot tactic detection
│   ├── emotional_tone.py          # Emotion classification
│   ├── logical_coherence.py       # Semantic coherence
│   ├── language_metrics.py        # Language complexity
│   ├── create_report_tables.py    # Generate result tables
│   └── create_language_complexity_table.py
├── config/                 # Configuration settings
│   └── config.py
├── personas/               # Persona definitions
│   └── persona_configs.py
├── scenarios/              # Negotiation scenarios
│   └── used_car_sale.json
├── simulation/             # Negotiation runner
│   └── realtime_negotiation.py
├── utils/                  # Utility modules
│   ├── mongodb_client.py   # Database interface
│   └── scenario_loader.py
├── app.py                  # Streamlit web interface
├── run_batch_tests.py      # Batch experiment runner
├── recalculate_tactics.py  # Recompute persuasion tactics
├── recalculate_language_metrics.py  # Recompute language metrics
├── requirements.txt        # Python dependencies
├── env.template            # Environment variables template
├── FINAL_REPORT_CONDENSED.tex  # LaTeX report (4-8 pages)
└── table*.csv             # Experimental results (5 tables)
```

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10+
- MongoDB (local or cloud instance)
- OpenAI API key (GPT-4o and GPT-4 access)

### Step 1: Clone Repository

```bash
git clone https://github.com/4lirastegar/Negotiation-table.git
cd Negotiation-table
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
cp env.template .env
# Edit .env with your credentials:
# OPENAI_API_KEY=your_openai_key
# MONGO_URI=your_mongodb_uri (default: mongodb://localhost:27017/)
# MONGO_DB_NAME=negotiation
```

### Step 5: Download NLP Models

The first run will automatically download required models:
- `MoritzLaurer/deberta-v3-large-zeroshot-v2.0` (~1.5GB)
- `j-hartmann/emotion-english-distilroberta-base` (~300MB)
- `sentence-transformers/all-MiniLM-L6-v2` (~90MB)
- NLTK data packages

---

## 🔬 Reproducing Experiments

### Option 1: Run Web Interface (Recommended for Exploration)

```bash
streamlit run app.py
```

Navigate to `http://localhost:8501` to:
- Run individual negotiations with custom personas
- View real-time message exchanges
- Inspect qualitative metrics
- Download negotiation transcripts

### Option 2: Reproduce Full Experiment (60 Negotiations)

```bash
python3 run_batch_tests.py
```

This runs:
- 10 negotiations × 6 persona combinations
- Total: 60 negotiations (~30-45 minutes)
- Results saved to MongoDB
- Automatic qualitative analysis

### Option 3: Generate Result Tables

After running experiments:

```bash
# Generate all tables from MongoDB data
python3 analysis/create_report_tables.py

# Output: table1_strategies.csv, table2_emotions.csv, 
#         table3_coherence.csv, table4_utility.csv

# Generate language complexity table
python3 analysis/create_language_complexity_table.py

# Output: table5_language_complexity.csv
```

---

## 📊 Experimental Results

### Table 1: Negotiation Strategies by Persona

| Persona Pair | Persuasion | Cooperation | Compromise | Agreement Rate | Avg Rounds |
|--------------|------------|-------------|------------|----------------|------------|
| Fair vs Fair | 0.5 | 0.2 | 4.2 | 100% | 5.3 |
| Aggressive vs Aggressive | 2.0 | 0.1 | 4.7 | 90% | 8.1 |
| Liar vs Fair | 1.6 | 0.0 | 5.4 | 80% | 8.0 |

**Key Finding:** Compromise dominated all negotiations (M=4.2-5.4), while deception and pressure were completely absent due to RLHF training constraints.

### Table 2: Utility Outcomes by Persona

| Persona | Mean Utility | SD | N |
|---------|--------------|-----|---|
| Liar | 0.48 | 0.24 | 8 |
| Aggressive | 0.29 | 0.19 | 37 |
| Fair | 0.13 | 0.16 | 37 |
| Strategic | 0.00 | 0.00 | 10 |

**Key Finding:** Liar persona achieved highest utility through strategic persuasion and superior opponent awareness, while Fair prioritized cooperation over self-interest.

### Full Results

See complete experimental results in:
- `table1_strategies.csv` - Negotiation tactics by persona
- `table2_emotions.csv` - Emotional tone distribution
- `table3_coherence.csv` - Logical coherence scores
- `table4_utility.csv` - Utility outcomes
- `table5_language_complexity.csv` - Linguistic complexity
- `FINAL_REPORT_CONDENSED.tex` - Full academic report (compile with LaTeX)

---

## 🔧 Key Components

### 1. Agent System (`agents/agent.py`)

```python
from agents.agent import Agent

# Create negotiation agent with persona
agent = Agent(
    agent_name="Agent A",
    persona_name="Fair",
    scenario_public_info={...},
    agent_secrets={...}
)

# Generate message
message = agent.generate_message()
```

### 2. Judge System (`agents/judge.py`)

```python
from agents.judge import Judge

judge = Judge()

# Check agreement and extract prices
result = judge.check_agreement_quick(messages)
# Returns: {
#   "agreement_reached": bool,
#   "agreed_price": float,
#   "agent_a_offer": float,
#   "agent_b_offer": float
# }
```

### 3. Qualitative Analysis (`analysis/`)

```python
from analysis.persuasion_tactics import PersuasionTacticsAnalyzer
from analysis.emotional_tone import EmotionalToneAnalyzer
from analysis.logical_coherence import LogicalCoherenceAnalyzer

# Analyze negotiation tactics
tactics_analyzer = PersuasionTacticsAnalyzer()
results = tactics_analyzer.analyze_negotiation(messages)

# Analyze emotional tone
emotion_analyzer = EmotionalToneAnalyzer()
emotions = emotion_analyzer.analyze_negotiation(messages)

# Analyze logical coherence
coherence_analyzer = LogicalCoherenceAnalyzer()
coherence = coherence_analyzer.analyze_negotiation(messages)
```

---

## 📖 Academic Report

The complete research findings are documented in **`FINAL_REPORT_CONDENSED.tex`**.

### Compiling the Report

```bash
# Compile LaTeX document
pdflatex FINAL_REPORT_CONDENSED.tex
bibtex FINAL_REPORT_CONDENSED  # If using BibTeX
pdflatex FINAL_REPORT_CONDENSED.tex
pdflatex FINAL_REPORT_CONDENSED.tex
```

Or use an online LaTeX editor like [Overleaf](https://www.overleaf.com/).

### Report Structure

1. **Introduction** - Research question and related work
2. **Methodology** - Experimental design and analysis methods
3. **Results** - Quantitative and qualitative findings (5 tables)
4. **Discussion** - Evidence for genuine reasoning vs scripted imitation
5. **Conclusion** - Key insights and future work

---

## 🤖 AI Usage Disclaimer

Parts of this project have been developed with the assistance of **Anthropic's Claude (Sonnet 4.5)**. The AI was used to support the implementation of the multi-agent negotiation system, including:

- Code development for agent architecture and judge system with structured outputs
- Qualitative analysis modules (persuasion tactics, emotion analysis, coherence measurement)
- Data processing pipelines and MongoDB integration

All AI-generated code has been carefully reviewed, tested, and validated by me. The research question, experimental design, methodology, and interpretation of results reflect my own understanding and academic judgment. I take full responsibility for the final implementation and the accuracy and integrity of all reported findings.

---

## 📚 References

### Core Models & Libraries

- **DeBERTa Zero-Shot:** Laurer et al. (2024). [Less annotating, more classifying](https://doi.org/10.1017/pan.2023.20). Political Analysis.
- **Sentence-BERT:** Reimers & Gurevych (2019). Sentence embeddings using siamese BERT-networks. EMNLP.
- **Emotion Classification:** Hartmann et al. (2023). More than a feeling: Accuracy and application of sentiment analysis. International Journal of Research in Marketing.

### Negotiation Research

- Lewis et al. (2017). Deal or no deal? End-to-end learning of negotiation dialogues. EMNLP.
- Raiffa, H. (1982). The art and science of negotiation. Harvard University Press.

### RLHF Training

- Ouyang et al. (2022). Training language models to follow instructions with human feedback. NeurIPS.

---

## 🏗️ Project Design Principles

This project follows academic software engineering best practices:

- **Modular Architecture:** Separation of concerns (agents, analysis, utils, simulation)
- **Object-Oriented Design:** Classes for Agent, Judge, Analyzers
- **Reproducibility:** Seed control, environment configuration, documented experiments
- **Extensibility:** Easy to add new personas, scenarios, or analysis metrics
- **Clean Code:** Docstrings, type hints, clear function signatures

---

## 📝 License

This project is submitted as academic coursework for the Natural Language Processing course at the University of Milan. Code and data are provided for educational and research purposes.

---

## 📧 Contact

**Ali Rastegar Mojarad**  
Email: 4lirastegar4li@gmail.com  
GitHub: [github.com/4lirastegar](https://github.com/4lirastegar)  
University of Milan, Department of Computer Science

---

## 🙏 Acknowledgments

- Prof. Alfio Ferrara (Course Instructor)
- Dott. Sergio Picascia, Dott.ssa Elisabetta Rocchetti (Teaching Assistants)
- OpenAI (GPT-4o and GPT-4 API)
- Hugging Face (Pre-trained transformer models)

---

**Last Updated:** February 2026
