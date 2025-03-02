# 🎵 Music Deconstructor  

**Music Deconstructor** extracts vocals, drums, bass, and more from any song. Provide a YouTube URL, and the extracted tracks are stored in a PostgreSQL database for future retrieval.

## 🚀 Features  
✅ Extract vocals, drums, bass, and more  
✅ Store extracted tracks in a PostgreSQL database  
✅ View history of processed songs  

## 🛠 Tech Stack  
- **Frontend:** Vite + React ⚡  
- **Backend:** FastAPI 🐍  
- **Database:** PostgreSQL 🐘  
- **Audio Processing:** Spleeter 🎶  

## 📂 Project Structure  
```
📦 music-deconstructor  
 ┣ 📂 frontend  _(React + Vite frontend)_  
 ┣ 📂 spleeter  _(FastAPI backend + Spleeter integration)_  
 ┗ 📜 README.md _(This file!)_  
```

## 🔧 Setup (Temporary, This Section Will Need To Undergo Changes Soon)  

To run the project:  

```bash
# Backend Setup
cd backend
source ./bin/activate  # Activate virtual environment

# Install the Spleeter model for audio separation
cd pretrained_models
wget https://github.com/deezer/spleeter/releases/download/v1.4.0/4stems.tar.gz
tar -xzf 4stems.tar.gz && rm 4stems.tar.gz

# Start FastAPI backend
fastapi dev main.py 

# Frontend Setup
cd ../frontend
npm install  # Install dependencies
npm run dev -- --host  # Start frontend server
```

### Short YouTube Demo (A Very Rough Demo Indeed!)
[![Music Deconstructor Demo](https://github.com/user-attachments/assets/c65b8fa4-7c98-4386-bca6-08138ae6fcac)](https://www.youtube.com/watch?v=P8H_VBtxBtc)


