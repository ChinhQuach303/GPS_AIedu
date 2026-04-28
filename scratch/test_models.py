import requests
import json

def test_ollama(model_name):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_name,
        "prompt": "Say hello in 3 words.",
        "stream": False
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"Model {model_name} OK: {response.json()['response'].strip()}")
            return True
        else:
            print(f"Model {model_name} failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"Error testing {model_name}: {e}")
        return False

if __name__ == "__main__":
    t_ok = test_ollama("qwen2.5:7b")
    s_ok = test_ollama("qwen2.5:1.5b")
    if t_ok and s_ok:
        print("Cả 2 model hoạt động tốt.")
    else:
        exit(1)
