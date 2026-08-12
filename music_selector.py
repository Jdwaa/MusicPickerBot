import os

def analyze_mood(image_path):
    # Временно отключаем AI-анализ
    print("🔍 AI-анализ отключен (экономия памяти), используем neutral")
    return "neutral"

def search_music(mood, max_results=1):
    # Временно отключаем поиск музыки (пока не наладим память)
    print("🔍 Поиск музыки отключен (экономия памяти)")
    return None