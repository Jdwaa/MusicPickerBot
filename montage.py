import os
import requests
from moviepy import *
from moviepy.video.fx import FadeIn, FadeOut

def create_reel(user_folder, music_url=None):
    try:
        # 1. Собираем все медиафайлы
        media_files = [f for f in os.listdir(user_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4', '.mov'))]
        if not media_files:
            print("❌ Нет медиафайлов")
            return None

        media_files.sort()
        clips = []

        # 2. Загружаем каждый файл как клип
        for file_name in media_files:
            file_path = os.path.join(user_folder, file_name)
            ext = os.path.splitext(file_name)[1].lower()

            if ext in ('.jpg', '.jpeg', '.png'):
                clip = ImageClip(file_path).resized(height=1080).with_duration(3)
            elif ext in ('.mp4', '.mov'):
                clip = VideoFileClip(file_path).resized(height=1080)
            else:
                continue

            clips.append(clip)

        if not clips:
            print("❌ Не удалось загрузить клипы")
            return None

        # 3. Применяем переходы (без .fx)
        final_clips = []
        for i, clip in enumerate(clips):
            if i == 0:
                clip = FadeIn(clip, 0.5)
            if i == len(clips) - 1:
                clip = FadeOut(clip, 0.5)
            final_clips.append(clip)

        # 4. Склеиваем всё в одно видео (правильный способ!)
        final_video = concatenate_videoclips(final_clips, method="compose")

        # 5. Добавляем музыку (если есть)
        if music_url:
            try:
                response = requests.get(music_url, timeout=10)
                if response.status_code == 200:
                    music_path = os.path.join(user_folder, "temp_music.mp3")
                    with open(music_path, "wb") as f:
                        f.write(response.content)

                    audio_clip = AudioFileClip(music_path)
                    if audio_clip.duration < final_video.duration:
                        audio_clip = audio_clip.loop(duration=final_video.duration)
                    else:
                        audio_clip = audio_clip.subclipped(0, final_video.duration)

                    audio_clip = audio_clip.with_volume_scaled(0.7)
                    final_video = final_video.with_audio(audio_clip)
                    os.remove(music_path)
            except Exception as e:
                print(f"⚠️ Ошибка с музыкой: {e}")

        # 6. Сохраняем видео
        user_id = os.path.basename(user_folder)
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"reel_{user_id}.mp4")

        final_video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            threads=4,
            logger=None
        )

        print(f"✅ Видео сохранено: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Ошибка монтажа: {e}")
        return None