"""
Configuration file for API keys and settings
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# LLM Settings
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo")  # Better reasoning than gpt-4o-mini

# MongoDB Settings
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST", "cluster0.mongodb.net")  # Default MongoDB Atlas host
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")  # Optional: full connection string

# Simulation Settings
MAX_ROUNDS = 10
TIMEOUT_SECONDS = 60
