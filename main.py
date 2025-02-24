import openai
import os
from moviepy import VideoFileClip, AudioFileClip
import streamlit as st



def transcribe_audio(audio_chunk_path):
    
    openai.api_key = st.secrets["openai_api_key"]
    
    with open(audio_chunk_path, "rb") as audio_file:
        transcription = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text",
            #prompt="Transcribe the following audio file and provide the text even if it is in mixed languages. Try not to miss any words."
        )
    return transcription



def extract_audio(video_path, audio_path):
    
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)
    audio_clip = clip.audio
    audio_clip.write_audiofile(audio_path.replace(".wav", ".mp3"), codec='mp3')
    clip.close()



def split_audio(audio_path, chunk_length=120):
    
    audio = AudioFileClip(audio_path)
    chunks = []
    duration = int(audio.duration)
    
    for i in range(0, duration, chunk_length):
        chunk = audio.subclipped(i, min(i + chunk_length, duration))
        chunk_path = f"temp/chunk_{i}.mp3"
        chunk.write_audiofile(chunk_path)
        chunks.append(chunk_path)
    
    return chunks



def main():
    st.title("Video to Text Transcription")
    
    video_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])
    
    if video_file is not None:
        video_file_path = f"temp/{video_file.name}"
        with open(video_file_path, "wb") as f:
            f.write(video_file.read())
        
        audio_file_path = "extracted_audio.mp3"
        
        # Extract audio from the video
        extract_audio(video_file_path, audio_file_path)
        
        # Split audio into smaller chunks
        audio_chunks = split_audio(audio_file_path, chunk_length=60)
        
        # Transcribe each chunk and combine results
        full_transcript = ""
        
        for chunk in audio_chunks:
            transcript = transcribe_audio(chunk)
            full_transcript += transcript + "\n"
            os.remove(chunk)  # Clean up chunk file after transcription
        
        # Display final transcription
        st.subheader("Transcription Result:")
        st.text_area("Transcription", full_transcript, height=300)
        
        # Clean up
        os.remove(video_file_path)
        os.remove(audio_file_path)

if __name__ == "__main__":
    main()