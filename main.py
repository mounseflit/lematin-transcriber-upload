import openai
import os
import streamlit as st
from moviepy import VideoFileClip, AudioFileClip
from mutagen.mp3 import MP3

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
    try:
        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_path)
        clip.close()
    except Exception as e:
        st.error(f"Erreur lors de l'extraction audio : {e}")

def split_audio(audio_path, duration, chunk_length=60):
    chunks = []
    
    try:
        audio = AudioFileClip(audio_path)
        os.makedirs("temp", exist_ok=True)  # Ensure temp directory exists
        
        for i in range(0, int(duration), chunk_length):
            chunk = audio.subclipped(i, min(i + chunk_length, duration))
            chunk_path = f"temp/chunk_{i}.mp3"
            chunk.write_audiofile(chunk_path)
            chunks.append(chunk_path)
        
        return chunks
    except Exception as e:
        st.error(f"Erreur lors du découpage de l'audio : {e}")
        return []

def remove_if_exists(file_path):
    """Utility function to remove a file if it exists."""
    if os.path.exists(file_path):
        os.remove(file_path)

def clean_temp_folder(folder="temp"):
    """Utility function to clean up all temporary files."""
    if os.path.exists(folder):
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            os.remove(file_path)


def main():
    st.title("🎙️ Transcripteur des Vidéos et Audio Le Matin")
    uploaded_file = st.file_uploader("Upload a video or audio file (200MB)", type=["mp4", "mp3"])

    if uploaded_file is not None:
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)  # Ensure the directory exists
        
        # Set file paths
        video_file_path = os.path.join(temp_dir, "uploaded_video.mp4")
        audio_file_path = os.path.join(temp_dir, "extracted_audio.mp3")

        # Save uploaded file to disk
        file_extension = uploaded_file.name.split(".")[-1]
        file_path = os.path.join(temp_dir, f"uploaded_file.{file_extension}")

        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        # Extract audio if it's a video
        if uploaded_file.type.startswith('video/'):
            extract_audio(file_path, audio_file_path)
        elif uploaded_file.type == 'audio/mpeg':
            audio_file_path = file_path  # Directly use uploaded audio
        else:
            st.error("Type de fichier non supporté. Veuillez uploader une vidéo ou un fichier audio.")
            return

        if not os.path.exists(audio_file_path):
            st.error("Erreur : Le fichier audio n'a pas été généré correctement.")
            return

        st.info("📝 Transcription en cours...")

        try:
            audio = MP3(audio_file_path)
            duration = int(audio.info.length)
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier audio : {e}")
            return

        # Split audio
        audio_chunks = split_audio(audio_file_path, duration, chunk_length=60)
        
        if not audio_chunks:
            st.error("Erreur lors de la découpe de l'audio.")
            return
        
        # Transcribe each chunk
        full_transcript = ""
        for chunk in audio_chunks:
            try:
                transcript = transcribe_audio(chunk)
                full_transcript += transcript + "\n"
                os.remove(chunk)  # Remove chunk after transcription
            except Exception as e:
                st.error(f"Erreur lors de la transcription d'un segment audio : {e}")

        st.success("✅ Transcription terminée !")
        st.subheader("Transcription :")
        st.text_area("📜 Texte Transcrit", full_transcript, height=300)
        st.download_button("⬇️ Télécharger la transcription", full_transcript, file_name="transcription.txt")

        # Clean any existing files
        remove_if_exists(file_path)
        remove_if_exists(video_file_path)
        remove_if_exists(audio_file_path)
        
        # Final cleanup
        clean_temp_folder(temp_dir)

if __name__ == "__main__":
    main()


# import openai
# import os
# import streamlit as st
# from moviepy import VideoFileClip, AudioFileClip
# from mutagen.mp3 import MP3



# def transcribe_audio(audio_chunk_path):
#     openai.api_key = st.secrets["OPENAI_API_KEY"]  # Use Streamlit secrets for security
    
#     with open(audio_chunk_path, "rb") as audio_file:
#         transcription = openai.audio.transcriptions.create(
#             model="whisper-1",
#             file=audio_file,
#             response_format="text",
#         )
#     return transcription

# def extract_audio(video_path, audio_path):
#     clip = VideoFileClip(video_path)
#     clip.audio.write_audiofile(audio_path)
#     clip.close()

# def split_audio(audio_path, duration, chunk_length=60):
   
#     chunks = []
#     audio = AudioFileClip(audio_path)
    
#     for i in range(0, duration, chunk_length):
#         chunk = audio.subclipped(i, min(i + chunk_length, duration))
#         chunk_path = f"temp/chunk_{i}.mp3"
#         chunk.write_audiofile(chunk_path)
#         chunks.append(chunk_path)
    
#     return chunks


# def main():
#     st.title("Transcripteur des Vidéos et Audio Le Matin")
#     uploaded_file = st.file_uploader("Upload a video or audio file (200MB)", type=["mp4", "mp3"])
                                                                           
#     if uploaded_file is not None:
#         video_file_path = "uploaded_video.mp4"
#         audio_file_path = "extracted_audio.mp3"
        
        
#         # Extract audio
#         if uploaded_file.type.startswith('video/'):
#             with open(video_file_path, "wb") as f:
#                 f.write(uploaded_file.read())
#             extract_audio(video_file_path, audio_file_path)
#         elif uploaded_file.type == 'audio/mpeg':
#             with open(audio_file_path, "wb") as f:
#                 f.write(uploaded_file.read())
#             audio_file_path = video_file_path
#         else:
#             st.error("Unsupported file type. Please upload a video or audio.")

#         st.info("📝 Transcription en cours...")

#         audio = MP3(audio_file_path)
#         duration = audio.info.length
#         st.text_area("duree", duration, height=100)
        
        
#         # Split audio
#         audio_chunks = split_audio(audio_file_path, duration, chunk_length=60)
        
#         # Transcribe each chunk
#         full_transcript = " "
#         for chunk in audio_chunks:
#             transcript = transcribe_audio(chunk)
#             full_transcript += transcript + "\n"
#             os.remove(chunk)
            
#         st.success("✅ Transcription terminée !")
#         st.subheader("Transcription Result:")
#         st.text_area("📜 Texte Transcrit", full_transcript, height=300)
#         st.download_button("⬇️ Télécharger la transcription", full_transcript, file_name="transcription.txt")
        
#         os.remove(audio_file_path)  # Nettoyage audio
#         os.remove(video_file_path)  # Nettoyage video

# if __name__ == "__main__":
#     main()
