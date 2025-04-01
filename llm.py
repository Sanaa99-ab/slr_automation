# llm.py
import requests
from config import config

def generate_research_questions(topic: str) -> list[str]:
    url = f"https://api-inference.huggingface.co/models/{config.HF_MODEL}"
    headers = {"Authorization": f"Bearer {config.HF_API_KEY}"}
    prompt = f"Generate 3 research questions about '{topic}' for a systematic literature review."
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 100, "num_return_sequences": 3}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        results = response.json()
        questions = [r["generated_text"].replace(prompt, "").strip() for r in results]
        return questions[:3]
    except Exception as e:
        return [
            f"Error: Could not generate questions ({str(e)})",
            f"Fallback: What is the impact of {topic} on X?",
            f"Fallback: How does {topic} influence Y?"
        ]

def propose_criteria(topic: str) -> list[str]:
    return [
        "Include: Papers in English",
        "Include: Published after 2015",
        "Exclude: Non-peer-reviewed articles"
    ]