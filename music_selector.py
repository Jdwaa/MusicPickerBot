import os
import requests
from PIL import Image
from io import BytesIO

# ==========================================
# ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ
# ==========================================
HF_TOKEN = os.getenv("HF_TOKEN")
FREESOUND_TOKEN = os.getenv("FREESOUND_API_KEY")

if not HF_TOKEN:
    raise ValueError("❌ HF_TOKEN не найден!")
if not FREESOUND_TOKEN:
    raise ValueError("❌ FREESOUND_API_KEY не найден!")

# ==========================================
# 1. АНАЛИЗ НАСТРОЕНИЯ ЧЕРЕЗ CLIP (Hugging Face)
# ==========================================
MODEL = "openai/clip-vit-base-patch32"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"

def analyze_mood(image_path):
    """
    Анализирует фото и возвращает настроение: romantic, energetic, calm, sad, neutral
    """
    try:
        with open(image_path, "rb") as f:
            data = f.read()

        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        response = requests.post(API_URL, headers=headers, data=data)

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
        print(f"❌ Ошибка при анализе фото: {e}")
        return "neutral"

# ==========================================
# 2. ПОИСК МУЗЫКИ ЧЕРЕЗ FREESOUND
# ==========================================
FREESOUND_SEARCH_URL = "https://freesound.org/apiv2/search/text/"

def search_music(mood, max_results=3):
    """
    Ищет треки на Freesound по настроению.
    Возвращает URL первого трека или None.
    """
    # Сопоставляем настроение с тегами для поиска
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
        response = requests.get(FREESOUND_SEARCH_URL, params=params)
        if response.status_code != 200:
            print(f"⚠️ Ошибка Freesound API: {response.status_code}")
            return None

        data = response.json()
        results = data.get("results", [])

        if not results:
            print("⚠️ Треки не найдены, пробуем fallback-поиск")
            # Fallback: ищем без фильтра лицензии
            params.pop("filter")
            response = requests.get(FREESOUND_SEARCH_URL, params=params)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

        for sound in results:
            previews = sound.get("previews", {})
            mp3_url = previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3")
            if mp3_url:
                return mp3_url

        return None

    except Exception as e:
        print(f"❌ Ошибка поиска музыки: {e}")
        return None

# ==========================================
# 3. ПРОВЕРКА РАБОТЫ (для локального теста)
# ==========================================
if __name__ == "__main__":
    # Тест: анализ фото и поиск музыки
    test_image = "test.jpg"  # замени на путь к своему фото
    if os.path.exists(test_image):
        mood = analyze_mood(test_image)
        print(f"Настроение: {mood}")
        music_url = search_music(mood)
        print(f"Музыка: {music_url}")
    else:
        print("Создай test.jpg для проверки")