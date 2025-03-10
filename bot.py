import telebot
import requests
import os
from pydub import AudioSegment

# Set FFmpeg and FFprobe path for Heroku
AudioSegment.converter = "/app/vendor/ffmpeg/ffmpeg"
AudioSegment.ffprobe   = "/app/vendor/ffmpeg/ffprobe"

# Telegram Bot Token
BOT_TOKEN = "7292774770:AAGzEgqEhkXkaN6KMkYofTcYkJOoG1DdTOs"

# RapidAPI API Headers
HEADERS = {
    'x-rapidapi-key': "b689fbd269mshfcdc75a663eb40ap1b3393jsnaa5ce053d101",
    'x-rapidapi-host': "ai-girlfriend-voice.p.rapidapi.com"
}

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

        # Convert OGG to WAV (required by API)
        wav_file = f"voices/{message.from_user.id}.wav"
        sound = AudioSegment.from_file(voice_file, format="ogg")
        sound.export(wav_file, format="wav")

        # Send request to AI API for voice conversion
        with open(wav_file, "rb") as f:
            api_response = requests.post("https://ai-girlfriend-voice.p.rapidapi.com/convert",
                                         headers=HEADERS, files={"file": f})

        if api_response.status_code == 200:
            output_voice = f"voices/{message.from_user.id}_girl.ogg"
            with open(output_voice, "wb") as f:
                f.write(api_response.content)

            bot.send_voice(message.chat.id, open(output_voice, "rb"))
        else:
            bot.send_message(message.chat.id, "Error converting voice. Please try again later.")

        # Clean up temporary files
        os.remove(voice_file)
        os.remove(wav_file)
    else:
        bot.send_message(message.chat.id, "Failed to download voice message.")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Send a voice message, and I will convert it to a girl's voice!")


bot.polling()
