import requests
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from core.config_utils import load_key
import json

def fish_tts(text: str, save_as: str) -> bool:
    """302.ai Fish TTS conversion"""
    API_KEY = load_key("fish_tts.api_key")
    character = load_key("fish_tts.character")
    refer_id = load_key("fish_tts.character_id_dict")[character]
    
    url = "https://api.302.ai/fish-audio/v1/tts"
    payload = json.dumps({
        "text": text,
        "reference_id": refer_id,
        "chunk_length": 200,
        "normalize": True,
        "format": "wav",
        "latency": "normal"
    })
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        response_data = response.json()
        
        if "url" in response_data:
            audio_response = requests.get(response_data["url"])
            audio_response.raise_for_status()
            
            with open(save_as, "wb") as f:
                f.write(audio_response.content)
            return True
        
        print("Request failed:", response_data)
        return False
        
    except Exception as e:
        print(f"Error in fish_tts: {str(e)}")
        return False

if __name__ == '__main__':
    fish_tts("Hi! Welcome to VideoLingo!", "test.wav")
