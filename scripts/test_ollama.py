"""
Simple script to test if Ollama is properly installed and responding.
Usage:
    python scripts/test_ollama.py
"""

import ollama

def test_ollama_connection():
    """Test basic Ollama functionality."""
    try:
        # Test basic model listing
        models = ollama.list()
        print("✓ Successfully connected to Ollama")
        print("\nAvailable models:")
        for model in models.get('models', []):
            print(f"- {model.get('name', 'Unknown')}")
        
        # Test basic query
        print("\nTesting basic query...")
        response = ollama.chat(model='llama3.2',
            messages=[{
                'role': 'user',
                'content': 'Hi, this is a test message. Please respond with a short greeting.'
            }]
        )
        print("\nOllama response:", response['message']['content'])
        print("\n✓ Ollama is working correctly!")
        
    except Exception as e:
        print("✗ Error connecting to Ollama:")
        print(f"  {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    test_ollama_connection()