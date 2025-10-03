import os, random, requests, textwrap
from gtts import gTTS
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# ================== CONFIG ==================
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
VIDEO_DIR = "videos"
THUMBNAIL_DIR = "thumbnails"
STOCK_DIR = "stock"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)
os.makedirs(STOCK_DIR, exist_ok=True)

# ================== STEP 1: AI SCRIPT ==================
def generate_ai_script():
    topics = [
        "How AI Side Hustles Can Make You $500/day",
        "Top 3 Free AI Tools You Must Try",
        "How to Automate Work with AI Agents",
        "Secret AI Techniques to Grow Online",
        "The Future of AI Money Making Hustles"
    ]
    title = random.choice(topics)
    body = f"""
    Welcome to today's video on {title}.
    In this video, we'll break down how you can use AI tools and automation 
    to create unique hustles and make passive income. 
    Stay tuned till the end because I’ll reveal a free tool that nobody talks about.
    """
    return title, body

# ================== STEP 2: TEXT TO SPEECH ==================
def text_to_speech(text, filename):
    tts = gTTS(text=text, lang="en")
    audio_path = os.path.join(VIDEO_DIR, filename + ".mp3")
    tts.save(audio_path)
    return audio_path

# ================== STEP 3: FETCH STOCK MEDIA ==================
def fetch_stock_media(query="artificial intelligence", count=3):
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page={count}"
    r = requests.get(url, headers=headers).json()
    paths = []
    for idx, video in enumerate(r.get("videos", [])):
        video_url = video["video_files"][0]["link"]
        path = os.path.join(STOCK_DIR, f"stock{idx}.mp4")
        with open(path, "wb") as f:
            f.write(requests.get(video_url).content)
        paths.append(path)
    return paths

# ================== STEP 4: VIDEO CREATION ==================
def create_video(title, body):
    audio_path = text_to_speech(body, "narration")
    narration = AudioFileClip(audio_path)

    stock_clips = fetch_stock_media("artificial intelligence", 3)
    clips = [VideoFileClip(p).resize((1280,720)) for p in stock_clips]
    bg_video = concatenate_videoclips(clips).subclip(0, narration.duration)

    txt_clip = TextClip(title, fontsize=60, color='yellow', size=(1200, None), method='caption')
    txt_clip = txt_clip.set_duration(narration.duration).set_position(("center","bottom"))

    final = CompositeVideoClip([bg_video, txt_clip])
    final = final.set_audio(narration)

    video_path = os.path.join(VIDEO_DIR, "final_video.mp4")
    final.write_videofile(video_path, fps=24)
    return video_path

# ================== STEP 5: SEO METADATA ==================
def generate_seo_metadata(title):
    seo_title = title + " | AI Hustles 2025"
    description = f"""
    Discover how to leverage AI tools, automation, and free apps to create unique side hustles.
    In this video: {title}.
    
    🚀 Subscribe for daily AI Hustle hacks!
    #AI #SideHustle #Automation
    """
    tags = ["AI tools", "side hustles", "make money online", "automation", "AI 2025", "passive income"]
    return seo_title, description, ",".join(tags)

# ================== STEP 6: THUMBNAIL CREATION ==================
def generate_thumbnail():
    thumb_texts = [
        "AI Trick = $$$",
        "Secret AI Hack!",
        "Make $500/day with AI",
        "Nobody Tells You This!",
        "AI Hustle Exposed!"
    ]
    thumb_text = random.choice(thumb_texts)
    img = Image.new("RGB", (1280, 720), color=(20,20,20))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    wrapped_text = textwrap.fill(thumb_text, width=20)
    draw.text((50,300), wrapped_text, font=font, fill="yellow")
    thumb_path = os.path.join(THUMBNAIL_DIR, "thumbnail.jpg")
    img.save(thumb_path)
    return thumb_path

# ================== STEP 7: AUTH + UPLOAD ==================
def get_authenticated_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def upload_video(video_path, title, description, tags, thumbnail_path):
    youtube = get_authenticated_service()

    request_body = {
        "snippet": {
            "categoryId": "28",
            "title": title,
            "description": description,
            "tags": tags.split(",")
        },
        "status": {"privacyStatus": "public"}
    }

    media_file = MediaFileUpload(video_path)
    response = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    ).execute()

    video_id = response.get("id")
    youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(thumbnail_path)
    ).execute()
    print(f"✅ Uploaded: https://youtube.com/watch?v={video_id}")

# ================== MAIN ==================
def main():
    title, body = generate_ai_script()
    video_path = create_video(title, body)
    seo_title, description, tags = generate_seo_metadata(title)
    thumb_path = generate_thumbnail()
    upload_video(video_path, seo_title, description, tags, thumb_path)

if __name__ == "__main__":
    main()
