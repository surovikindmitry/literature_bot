import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    AI_MODEL = os.getenv('AI_MODEL')
    AI_PROMPT = os.getenv('AI_PROMPT')
    ADMIN_CHANNEL_ID = os.getenv('ADMIN_CHANNEL_ID')

config = Config()