"""
Quick test script to verify Gemini embeddings work.
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY not found in .env")
    exit(1)

print(f"API Key found: {api_key[:20]}...")
genai.configure(api_key=api_key)

# Test different model names
models_to_test = [
    "models/text-embedding-004",
    "models/embedding-001",
    "models/text-embedding-004",
    "text-embedding-004",
]

test_text = "This is a test of the Gemini embedding API."

for model in models_to_test:
    print(f"\n{'='*60}")
    print(f"Testing model: {model}")
    print(f"{'='*60}")
    try:
        result = genai.embed_content(
            model=model,
            content=test_text,
            task_type="retrieval_document",
        )
        print(f"✓ SUCCESS! Embedding dimension: {len(result['embedding'])}")
        print(f"First 5 values: {result['embedding'][:5]}")

        # If successful, save this model name
        with open(".working_model.txt", "w") as f:
            f.write(model)
        print(f"\n✓ Saved working model: {model}")
        break

    except Exception as e:
        print(f"✗ FAILED: {e}")

# Also list available models
print(f"\n{'='*60}")
print("Available models from API:")
print(f"{'='*60}")
try:
    for model in genai.list_models():
        if "embed" in model.name.lower():
            print(f"  - {model.name}: {model.display_name}")
            print(f"    Supported methods: {model.supported_generation_methods}")
except Exception as e:
    print(f"Error listing models: {e}")
