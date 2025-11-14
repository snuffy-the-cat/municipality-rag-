"""
Test script to check which libraries are available in the venv
"""

print("Testing imports...\n")

# Test basic libraries
try:
    import yaml
    print("[OK] pyyaml - INSTALLED")
except ImportError as e:
    print(f"[FAIL] pyyaml - NOT INSTALLED: {e}")

try:
    from dotenv import load_dotenv
    print("[OK] python-dotenv - INSTALLED")
except ImportError as e:
    print(f"[FAIL] python-dotenv - NOT INSTALLED: {e}")

try:
    import requests
    print("[OK] requests - INSTALLED")
except ImportError as e:
    print(f"[FAIL] requests - NOT INSTALLED: {e}")

try:
    from pydantic import BaseModel
    print("[OK] pydantic - INSTALLED")
except ImportError as e:
    print(f"[FAIL] pydantic - NOT INSTALLED: {e}")

# Test LLM libraries
try:
    import ollama
    print("[OK] ollama - INSTALLED")
except ImportError as e:
    print(f"[FAIL] ollama - NOT INSTALLED: {e}")

try:
    import openai
    print("[OK] openai - INSTALLED")
except ImportError as e:
    print(f"[FAIL] openai - NOT INSTALLED: {e}")

try:
    import anthropic
    print("[OK] anthropic - INSTALLED")
except ImportError as e:
    print(f"[FAIL] anthropic - NOT INSTALLED: {e}")

# Test langchain
try:
    import langchain
    print("[OK] langchain - INSTALLED")
except ImportError as e:
    print(f"[FAIL] langchain - NOT INSTALLED: {e}")

try:
    from langchain_community.llms import Ollama
    print("[OK] langchain-community - INSTALLED")
except ImportError as e:
    print(f"[FAIL] langchain-community - NOT INSTALLED: {e}")

# Test chromadb
try:
    import chromadb
    print("[OK] chromadb - INSTALLED")
except ImportError as e:
    print(f"[FAIL] chromadb - NOT INSTALLED: {e}")

# Test utilities
try:
    from tqdm import tqdm
    print("[OK] tqdm - INSTALLED")
except ImportError as e:
    print(f"[FAIL] tqdm - NOT INSTALLED: {e}")

try:
    from loguru import logger
    print("[OK] loguru - INSTALLED")
except ImportError as e:
    print(f"[FAIL] loguru - NOT INSTALLED: {e}")

print("\n" + "="*50)
print("Import test complete!")
print("="*50)
