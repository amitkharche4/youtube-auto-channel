import os
import random
import logging
import requests
import base64
from datetime import datetime
from gtts import gTTS
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
from PIL import Image, ImageDraw, ImageFont
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json

# ------------------ Logging ------------------
logging.basicConfig(
    filename="uploader.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ------------------ Settings ------------------
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")  # stored in GitHub Secrets
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# ------------------ SEO AI Generator (simulated GPT) ------------------
def generate_ai_content():
    """Generate AI Hustle video content (title, desc, tags)."""
    ideas = [
        "AI Side Hustles Nobody Talks About",
        "How to Make $500/Day with Free AI Tools",
        "Unique AI Business Ideas for 2025",
        "Hidden AI Hustles That Actually Pay",
        "Earn Passive Income with AI (Zero Cost)"
    ]
    title = random.choice(ideas)
    desc = (
        f"{title}\n\n"
        f"Discover the latest AI hustle you can start today with zero investment. "
        f"Daily uploads about AI tools, automation and hidden income streams.\n\n"
        f"#AI #SideHustle #MakeMoneyOnline"
    )
    tags = ["AI Hustle", "Make Money Online", "AI Tools", "Passive Income", "Side Hustle 2025"]
    return title, desc, tags

# ------------------ Stock Media Downloader ------------------
def download_stock_image():
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": "artificial intelligence technology", "per_page": 1}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    img_url = data["photos"][0]["src"]["large"]
    img_data = requests.get(img_url).content
    with open("background.jpg", "wb") as f:
        f.write(img_data)
    logging.info("Downloaded stock background image.")

# ------------------ Audio Generation ------------------
def create_tts_audio(text):
    tts = gTTS(text=text, lang="en")
    tts.save("voice.mp3")
    logging.info("Generated voiceover with gTTS.")

# ------------------ Video Creation ------------------
def create_video():
    image = ImageClip("background.jpg", duration=30)
    audio = AudioFileClip("voice.mp3")
    video = image.set_audio(audio)
    video.write_videofile("output.mp4", fps=24)
    logging.info("Created final video output.mp4.")

# ------------------ Thumbnail Generator ------------------
def create_thumbnail(title):
    img = Image.new("RGB", (1280, 720), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((50, 300), title[:40], font=font, fill="white")
    img.save("thumbnail.jpg")
    logging.info("Created CTR-boosting thumbnail.")

# ------------------ YouTube Upload ------------------
def authenticate_youtube():
    creds = None
    if os.path.exists("token.json"):
        with open("token.json", "r") as token:
            creds_data = json.load(token)
            from google.oauth2.credentials import Credentials
            creds = Credentials.from_authorized_user_info(creds_data, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

def upload_to_youtube(title, desc, tags):
    youtube = authenticate_youtube()
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": desc,
                "tags": tags,
                "categoryId": "28"  # Science & Technology
            },
            "status": {"privacyStatus": "public"}
        },
        media_body="output.mp4"
    )
    response = request.execute()
    logging.info(f"Uploaded video to YouTube: {response['id']}")

# ------------------ Main Pipeline ------------------
def main():
    try:
        title, desc, tags = generate_ai_content()
        download_stock_image()
        create_tts_audio(desc)
        create_video()
        create_thumbnail(title)
        upload_to_youtube(title, desc, tags)
        logging.info("✅ Pipeline finished successfully.")
    except HttpError as e:
        logging.error(f"YouTube API error: {e}")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()

