import os
import requests
from PIL import Image
from io import BytesIO

HF_TOKEN = os.getenv("HF_TOKEN")
FREESOUND_TOKEN = os.getenv("FREESOUND_API_KEY")

if not HF_TOKEN:
    raise ValueError("❌ HF_TOKEN не найден!")
if not FREESOUND_TOKEN:
    raise ValueError("❌ FREESOUND_API_KEY не найден!")

MODEL = "openai/clip-vit-base-patch32"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"

def analyze_mood(image_path):
    try:
        with open(image_path, "rb") as f:
            data = f.read()

        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        response = requests.post(API_URL, headers=headers, data=data, timeout=10)

        if response.status_code != 200:
            print(f"⚠️ Ошибка HF API: {response.status_code}")
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
                "relaxed": "calm",
                "neutral": "neutral"
            }
            return mood_map.get(label, "neutral")
        return "neutral"

    except Exception as e:
        print(f"⚠️ Ошибка при анализе фото: {e}")
        return "neutral"

FREESOUND_SEARCH_URL = "https://freesound.org/apiv2/search/text/"

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
        response = requests.get(FREESOUND_SEARCH_URL, params=params, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Ошибка Freesound API: {response.status_code}")
            return None

        data = response.json()
        results = data.get("results", [])

        for sound in results:
            previews = sound.get("previews", {})
            mp3_url = previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3")
            if mp3_url:
                return mp3_url

        return None

    except Exception as e:
        print(f"⚠️ Ошибка поиска музыки: {e}")
        return None