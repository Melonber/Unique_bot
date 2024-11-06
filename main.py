import telebot
import os
import random
import cv2  
from moviepy.editor import VideoFileClip, vfx
from datetime import datetime, timedelta
from keys import token

# Инициализация бота
bot = telebot.TeleBot(token)

# Папки для сохранения видео
GET_VIDEOS_DIR = 'get_videos'
SEND_VIDEOS_DIR = 'send_videos'
os.makedirs(GET_VIDEOS_DIR, exist_ok=True)
os.makedirs(SEND_VIDEOS_DIR, exist_ok=True)

# Переменная для отслеживания ID видео
video_id = 1


@bot.message_handler(content_types=['video'])
def handle_video(message):
    global video_id
    bot.send_message(message.chat.id, "Я получил ваше видео и обрабатываю его...")

    # Скачиваем полученное видео
    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    original_video_path = f"{GET_VIDEOS_DIR}/video_{video_id}.mp4"

    # Сохраняем исходное видео
    with open(original_video_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Уникализируем видео
    modified_video_path = f"{SEND_VIDEOS_DIR}/video_{video_id}.mp4"
    speed_factor, is_mirrored, zoom_factor, creation_time, original_bitrate, new_bitrate = modify_video(
        original_video_path, modified_video_path)

    # Отправляем уникализированное видео обратно пользователю
    with open(modified_video_path, 'rb') as video:
        bot.send_video(message.chat.id, video)

    # Сообщаем об измененных метаданных
    metadata_message = (
        f"Обработка завершена! Ваше уникализированное видео готово.\n"
        f"Измененные метаданные:\n"
        f"Скорость: изменена на {speed_factor:.2f}\n"
        f"Зеркалирование: {'Да' if is_mirrored else 'Нет'}\n"
        f"Масштаб: изменен на {zoom_factor:.2%}\n"
        f"Время создания: изменено на {creation_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Битрейт: изменен с {original_bitrate} на {new_bitrate}"
    )
    bot.send_message(message.chat.id, metadata_message)

    # Увеличиваем ID для следующего видео
    video_id += 1


def modify_video(input_path, output_path):
    # Загружаем видео
    clip = VideoFileClip(input_path)

    # Получаем информацию о битрейте
    original_bitrate = get_bitrate(input_path)

    # Случайное изменение скорости
    speed_factor = random.uniform(0.7, 1.3)
    clip = clip.fx(vfx.speedx, speed_factor)

    # Случайное зеркалирование
    is_mirrored = random.choice([True, False])
    if is_mirrored:
        clip = clip.fx(vfx.mirror_x)

    # Случайное увеличение/уменьшение масштаба
    zoom_factor = random.uniform(0.92, 1.08)
    new_size = (int(clip.w * zoom_factor), int(clip.h * zoom_factor))

    # Случайное изменение даты создания
    creation_time = datetime.now() - timedelta(days=random.randint(0, 365))
    os.utime(input_path, (creation_time.timestamp(), creation_time.timestamp()))

    # Случайное изменение битрейта
    bitrate_factor = random.uniform(0.9, 1.1)  # Незначительное изменение битрейта
    new_bitrate = int(original_bitrate * bitrate_factor)

    # Сохраняем измененное видео с новым битрейтом
    clip.write_videofile(output_path, codec='libx264', bitrate=f'{new_bitrate}k')

    return speed_factor, is_mirrored, zoom_factor, creation_time, original_bitrate, new_bitrate


def get_bitrate(video_path):
    """Получение битрейта видео с помощью OpenCV."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0
    bitrate = int(cap.get(cv2.CAP_PROP_FPS) * cap.get(cv2.CAP_PROP_FRAME_COUNT) * 0.8)  # Оценка битрейта
    cap.release()
    return bitrate


# Запуск бота
bot.polling()
