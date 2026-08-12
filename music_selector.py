import os
import requests

HF_TOKEN = os.getenv("HF_TOKEN")
FREESOUND_TOKEN = os.getenv("FREESOUND_API_KEY")

def analyze_mood(image_path):
    try:
        with open(image_path, "rb") as f:
            data = f.read()

        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        response = requests.post(
            "https://api-inference.huggingface.co/models/openai/clip-vit-base-patch32",
            headers=headers,
            data=data,
            timeout=5
        )

        if response.status_code != 200:
            return "neutral"

        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            label = result[0].get("label", "neutral").lower()
            mood_map = {
                "romantic": "romantic",
                "love": "romantic",
                "joy": "energetic",
                "happiness": "energetic",
                "sadness": "sad",
                "sad": "sad",
                "calm": "calm",
                "relaxed": "calm"
            }
            return mood_map.get(label, "neutral")
        return "neutral"

    except Exception as e:
        print(f"⚠️ Ошибка анализа фото: {e}")
        return "neutral"

def search_music(mood, max_results=3):
    tag_map = {
        "romantic": "romantic",
        "energetic": "energetic",
        "calm": "calm",
        "sad": "sad",
        "neutral": "ambient"
    }
    tag = tag_map.get(mood, "ambient")

    params = {
        "query": tag,
        "filter": "license:('Creative Commons 0' OR 'CC0')",
        "fields": "id,name,previews",
        "page_size": max_results,
        "token": FREESOUND_TOKEN
    }

    try:
        response = requests.get("https://freesound.org/apiv2/search/text/", params=params, timeout=10)
        if response.status_code != 200:
            return None

        data = response.json()
        for sound in data.get("results", []):
            previews = sound.get("previews", {})
            mp3_url = previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3")
            if mp3_url:
                return mp3_url

        return None

    except Exception as e:
        print(f"⚠️ Ошибка Freesound: {e}")
        return None