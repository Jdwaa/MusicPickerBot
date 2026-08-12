import os
import gc
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

        # 2. Загружаем клипы
        clips = []
        for file_name in media_files:
            file_path = os.path.join(user_folder, file_name)
            ext = os.path.splitext(file_name)[1].lower()

            if ext in ('.jpg', '.jpeg', '.png'):
                clip = ImageClip(file_path).resized(height=720).with_duration(3)
            elif ext in ('.mp4', '.mov'):
                clip = VideoFileClip(file_path).resized(height=720)
            else:
                continue

            clips.append(clip)
            gc.collect()

        if not clips:
            print("❌ Не удалось загрузить клипы")
            return None

        # 3. Применяем переходы
        final_clips = []
        for i, clip in enumerate(clips):
            if i == 0:
                clip = FadeIn(clip, 0.5)
            if i == len(clips) - 1:
                clip = FadeOut(clip, 0.5)
            final_clips.append(clip)
            gc.collect()

        # 4. СКЛЕИВАЕМ ЧЕРЕЗ concatenate_videoclips (без +)
        final_video = concatenate_videoclips(final_clips, method="compose")
        gc.collect()

        # 5. Музыка
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
                    gc.collect()
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
            threads=2,
            logger=None,
            verbose=False
        )

        final_video.close()
        gc.collect()

        print(f"✅ Видео сохранено: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Ошибка монтажа: {e}")
        gc.collect()
        return None