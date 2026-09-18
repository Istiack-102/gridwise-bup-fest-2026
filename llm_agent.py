import os
import json
import requests
from dotenv import load_dotenv

# gitignore.env ফাইল থেকে API Key লোড করা
load_dotenv("gitignore.env")
api_key_raw = os.getenv("GROQ_API_KEY")

if not api_key_raw:
    print("Error: GROQ_API_KEY not found! Please check your gitignore.env file.")
    exit(1)

api_key = api_key_raw.strip()

def get_working_model():
    """সঠিক চ্যাট মডেল খুঁজে বের করার ফাংশন"""
    try:
        url = "https://api.groq.com/openai/v1/models"
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        models = response.json().get("data", [])
        
        model_ids = [m["id"] for m in models]
        print(f"Available models in your account: {model_ids}\n")
        
        # 'guard', 'vision' ইত্যাদি বাদ দিয়ে আসল চ্যাট মডেল খোঁজা
        for m_id in model_ids:
            mid = m_id.lower()
            if "guard" not in mid and "vision" not in mid and "whisper" not in mid and "tool" not in mid:
                if "llama" in mid or "gemma" in mid or "mixtral" in mid:
                    return m_id
                    
        if model_ids:
            return model_ids[0]
            
    except Exception as e:
        print("Model fetch error:", e)
    
    return "llama3-8b-8192"

ACTIVE_MODEL = get_working_model()
print(f"--- System using auto-detected model: {ACTIVE_MODEL} ---\n")

def interpret_operator_notes(notes: list[str]) -> list[dict]:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    You are a smart campus energy management AI. Analyze the following operator notes and convert them into structured JSON directives.
    
    Supported directive_types and their required structured_adjustment:
    - "solar_reduction": {{"hours": [int], "factor": float}} (factor is the usable fraction remaining, e.g., 80% reduction = 0.2)
    - "minimum_battery_reserve": {{"hours": [int], "minimum_energy_kwh": float}}
    - "no_charge_window": {{"hours": [int]}}
    - "no_discharge_window": {{"hours": [int]}}
    - "max_grid_window": {{"hours": [int], "max_grid_kwh": float}}
    - "no_op": For irrelevant notes.

    Rules:
    1. applies = true for all except "no_op". For "no_op", applies = false and structured_adjustment = null.
    2. Time ranges: "1 PM to 3 PM" means hours [13, 14] (start-inclusive, end-exclusive).
    3. Return exactly one interpretation entry for every operator note in the exact order (note_index 0, 1, 2...).
    4. hours array must contain unique integers from 0 to 23 in ascending order.
    
    Operator Notes to analyze:
    {json.dumps(notes)}
    
    You must output ONLY a valid JSON object containing a single key "directives". The value must be an array of objects matching this schema:
    {{
        "directives": [
            {{
                "note_index": int,
                "applies": bool,
                "directive_type": "str",
                "structured_adjustment": dict or null,
                "explanation": "str"
            }}
        ]
    }}
    """
    
    data = {
        "model": ACTIVE_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0.0
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result_json = response.json()
        llm_text = result_json['choices'][0]['message']['content']
        
        parsed_data = json.loads(llm_text)
        return parsed_data.get("directives", [])
        
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        if 'response' in locals():
            print(f"Response details: {response.text}")
        return []

# লোকালি টেস্ট করার জন্য
if __name__ == "__main__":
    sample_notes = [
        "Solar output will drop to about 20% from 1 PM to 3 PM.",
        "The cafeteria menu changes tomorrow."
    ]
    result = interpret_operator_notes(sample_notes)
    print(json.dumps(result, indent=2))