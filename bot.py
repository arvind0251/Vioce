import telebot
import os
import http.client
import requests
from pydub import AudioSegment

# Set FFmpeg and FFprobe path for Heroku
AudioSegment.converter = "/app/vendor/ffmpeg/ffmpeg"
AudioSegment.ffprobe = "/app/vendor/ffmpeg/ffprobe"

# Telegram Bot Token
BOT_TOKEN = "7292774770:AAGzEgqEhkXkaN6KMkYofTcYkJOoG1DdTOs"

# API Details
API_HOST = "ai-girlfriend-voice.p.rapidapi.com"
API_KEY = "b689fbd269mshfcdc75a663eb40ap1b3393jsnaa5ce053d101"

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Directory to store voice files
if not os.path.exists("voices"):
    os.makedirs("voices")


@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    bot.send_message(message.chat.id, "Processing your voice...")

    # Download the voice file
    file_info = bot.get_file(message.voice.file_id)
    file_path = file_info.file_path
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

    response = requests.get(file_url)
    if response.status_code == 200:
        voice_file = f"voices/{message.from_user.id}.ogg"
        with open(voice_file, 'wb') as f:
            f.write(response.content)

        # Convert OGG to WAV (16-bit PCM format for compatibility)
        wav_file = f"voices/{message.from_user.id}.wav"
        sound = AudioSegment.from_file(voice_file, format="ogg")
        sound = sound.set_frame_rate(16000).set_sample_width(2).set_channels(1)  # Ensure correct format
        sound.export(wav_file, format="wav")

        # Send request to AI API using the correct endpoint
        conn = http.client.HTTPSConnection(API_HOST)
        headers = {
            'x-rapidapi-key': API_KEY,
            'x-rapidapi-host': API_HOST,
            'Content-Type': 'application/octet-stream'
        }

        # Open the WAV file and read its content
        with open(wav_file, "rb") as f:
            file_data = f.read()

        # 🔹 Corrected API endpoint
        conn.request("POST", "/female-voices", body=file_data, headers=headers)
        res = conn.getresponse()
        api_response = res.read()

        # Debugging: Print API response
        print("API Response Status:", res.status)
        print("API Response Content:", api_response.decode())

        if res.status == 200:
            output_voice = f"voices/{message.from_user.id}_girl.ogg"
            with open(output_voice, "wb") as f:
                f.write(api_response)

            bot.send_voice(message.chat.id, open(output_voice, "rb"))
        else:
            bot.send_message(message.chat.id, f"Error converting voice: {api_response.decode()}")

        # Clean up temporary files
        os.remove(voice_file)
        os.remove(wav_file)
    else:
        bot.send_message(message.chat.id, "Failed to download voice message.")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Send a voice message, and I will convert it to a girl's voice!")


bot.polling()
