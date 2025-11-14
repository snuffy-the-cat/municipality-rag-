"""
Test Ollama connection and pull model if needed
"""

import ollama

print("Testing Ollama connection...\n")

try:
    # Test connection
    print("[1/3] Checking Ollama API...")
    response = ollama.list()
    print("[OK] Ollama is running!")

    # Check if llama3.1 is installed
    print("\n[2/3] Checking for llama3.1 model...")
    models = [model['name'] for model in response.get('models', [])]

    if any('llama3.1' in model for model in models):
        print("[OK] llama3.1 model found!")
    else:
        print("[INFO] llama3.1 not found. Pulling model...")
        print("This will download ~4.7GB. Please wait...")

        # Pull the model
        ollama.pull('llama3.1')
        print("[OK] llama3.1 model downloaded!")

    # Test generation
    print("\n[3/3] Testing generation...")
    result = ollama.generate(
        model='llama3.1',
        prompt='Say "hello" in one word',
        options={'num_predict': 5}
    )
    print(f"[OK] Test response: {result['response'][:50]}")

    print("\n" + "="*50)
    print("[SUCCESS] Ollama is ready for document generation!")
    print("="*50)
    print("\nYou can now run:")
    print("  python scripts/generate_documents.py")

except Exception as e:
    print(f"\n[FAIL] Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure Ollama app is running (check system tray)")
    print("2. Try restarting Ollama")
    print("3. Check if another process is using port 11434")
