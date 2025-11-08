"""Test Groq model fallback on rate limits."""

from backend.utils.groq_client import GroqLLMClient
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

print("="*80)
print("GROQ MODEL FALLBACK TEST")
print("="*80)
print()

# Initialize client
client = GroqLLMClient()

print(f"Initial model: {client.model}")
print(f"Available fallback models: {client.AVAILABLE_MODELS}")
print()

# Get model info
info = client.get_model_info()
print("Model Info:")
for key, value in info.items():
    print(f"  {key}: {value}")
print()

# Try a simple chat
print("Testing simple chat...")
try:
    response = client.chat_with_system(
        system_prompt="You are a helpful assistant.",
        user_message="Say 'Hello, I am working!' in 5 words or less."
    )
    print(f"✅ Response: {response}")
    print(f"✅ Current model after success: {client.model}")
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Current model after error: {client.model}")

print()
print("="*80)
print("Model fallback is now active!")
print("If rate limit is hit, it will automatically switch to:")
for i, model in enumerate(client.AVAILABLE_MODELS):
    prefix = "✓ ACTIVE" if i == client.current_model_index else f"  Fallback {i}"
    print(f"  {prefix}: {model}")
print("="*80)
