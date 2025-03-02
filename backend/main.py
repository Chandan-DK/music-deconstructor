from urllib.parse import quote
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import os
import threading
from spleeter.separator import Separator
import psycopg

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


# Initialize FastAPI app
app = FastAPI()

# Paths
DOWNLOAD_DIR = "/workspaces/python-8/downloads"
OUTPUT_DIR = "/workspaces/python-8/stems"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Serve extracted stems as static files
app.mount("/stems", StaticFiles(directory=OUTPUT_DIR), name="stems")

@app.get("/stems/{stem_filename}")
async def get_stem(stem_filename: str):
    stem_path = os.path.join(OUTPUT_DIR, stem_filename)
    if os.path.exists(stem_path):
        return FileResponse(stem_path, media_type="audio/wav")
    raise HTTPException(status_code=404, detail="Stem not found")

@app.on_event("startup")
def startup_event():
    print("Initializing Database... 🚀")
    init_db()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL connection details
DB_CONFIG = {
    "dbname": "stems_db",
    "user": "stems_user",
    "password": "newpwd",
    "host": "localhost",
    "port": 5432
}

# Create tables if they don't exist
def init_db():
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS stems (
                    id SERIAL PRIMARY KEY,
                    youtube_url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    stems_path TEXT NOT NULL,
                    extracted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

# Call DB initialization
init_db()

# YouTube Request Model
class YouTubeRequest(BaseModel):
    url: str

# Create a SINGLE global Separator instance
separator = Separator('spleeter:4stems')

# Use a Lock to prevent concurrent access issues
lock = threading.Lock()

# Download YouTube audio
def download_audio(youtube_url: str) -> str:
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}],
        'outtmpl': f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        filename = f"{info['title']}.wav"
        return os.path.join(DOWNLOAD_DIR, filename), info['title']

# Separate stems
def separate_audio(input_file: str) -> str:
    output_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(input_file))[0])

    with lock:  # Prevent concurrent separator issues
        separator.separate_to_file(input_file, OUTPUT_DIR)

    return output_path

def save_stem_info(youtube_url: str, song_name: str, stems_path: str):
    try:
        print("Attempting to connect to DB...")
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Check if the YouTube URL already exists
                cur.execute("SELECT * FROM stems WHERE youtube_url = %s;", (youtube_url,))
                existing_entry = cur.fetchone()

                if existing_entry:
                    print("Stems already exist in DB!")
                    return False  # Notify that the stems already exist

                # Insert new record
                cur.execute("""
                    INSERT INTO stems (youtube_url, title, stems_path)
                    VALUES (%s, %s, %s);
                """, (youtube_url, song_name, stems_path))
                conn.commit()
                return True  # Successfully inserted
    except Exception as e:
        print(f"Database error: {e}")
        return False


@app.post("/extract-stems/")
async def receive_youtube_link(request: YouTubeRequest):
    try:
        downloaded_file, song_name = download_audio(request.url)
        stems_path = separate_audio(downloaded_file)

        inserted = save_stem_info(request.url, song_name, stems_path)

        # Generate URLs for the extracted stems
        stem_files = ["vocals.wav", "drums.wav", "bass.wav", "other.wav"]

        stem_urls = {
            stem: f"http://127.0.0.1:8000/stems/{quote(os.path.basename(stems_path))}/{stem}"
            for stem in stem_files
        }

        print(stem_urls) # Remove later

        if not inserted:
            return {"message": "Stems already extracted!", "stems": stem_urls}

        return {"message": "Processing Complete!", "stems": stem_urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@app.get("/history/")
async def get_songs(skip: int = 0, limit: int = 10):
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT title, stems_path FROM stems ORDER BY extracted_date DESC LIMIT %s OFFSET %s;", (limit, skip))
            songs = cur.fetchall()

    result = []
    for title, stems_path in songs:
        # Extract all audio files inside the `stems_path` folder
        stems = {}
        if os.path.isdir(stems_path):
            for file in os.listdir(stems_path):
                if file.endswith((".mp3", ".wav")):
                    stem_name = os.path.splitext(file)[0]  # Extract name without extension
                    stems[stem_name] = f"http://127.0.0.1:8000/stems/{os.path.basename(stems_path)}/{file}"

        result.append({
            "title": title,
            "stems": stems  # Map of {stem_name: URL}
        })

    return result




