import openai
import os
import streamlit as st
from moviepy import VideoFileClip, AudioFileClip

def transcribe_audio(audio_chunk_path):
    openai.api_key = st.secrets["OPENAI_API_KEY"]  # Use Streamlit secrets for security
    
    with open(audio_chunk_path, "rb") as audio_file:
        transcription = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text",
        )
    return transcription

def extract_audio(video_path, audio_path):
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)
    clip.close()

def split_audio(audio_path, chunk_length=120):
    audio = AudioFileClip(audio_path)
    chunks = []
    duration = int(audio.duration)
    
    for i in range(0, duration, chunk_length):
        chunk = audio.subclip(i, min(i + chunk_length, duration))
        chunk_path = f"temp/chunk_{i}.mp3"
        chunk.write_audiofile(chunk_path)
        chunks.append(chunk_path)
    
    return chunks

def main():
    st.title("Video to Text Transcription App")
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])
    
    if uploaded_file is not None:
        video_file_path = "uploaded_video.mp4"
        audio_file_path = "extracted_audio.mp3"
        
        with open(video_file_path, "wb") as f:
            f.write(uploaded_file.read())
        
        # Extract and split audio
        extract_audio(video_file_path, audio_file_path)
        audio_chunks = split_audio(audio_file_path, chunk_length=60)
        
        # Transcribe each chunk
        full_transcript = ""
        for chunk in audio_chunks:
            transcript = transcribe_audio(chunk)
            full_transcript += transcript + "\n"
            os.remove(chunk)
        
        st.subheader("Transcription Result:")
        st.text_area("", full_transcript, height=300)

if __name__ == "__main__":
    main()
