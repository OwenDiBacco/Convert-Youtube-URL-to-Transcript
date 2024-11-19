import os
import uuid
import shutil
from pytubefix import YouTube
from pytubefix.cli import on_progress
import tkinter as tk
import moviepy.editor as mp
from pathlib import Path
import speech_recognition as sr
from pytube import Playlist
from pydub import AudioSegment
from pydub.silence import split_on_silence
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YouTube URL Input")

        label = tk.Label(self.root, text="Enter YouTube Video or Playlist URL:", font=("Arial", 14))
        label.pack(pady=10)

        self.url_entry = tk.Entry(self.root, width=50, font=("Arial", 12))
        self.url_entry.pack(pady=10)

        submit_button = tk.Button(self.root, text="Submit", font=("Arial", 12), command=self.get_url)
        submit_button.pack(pady=20)

        self.root.mainloop()

    def get_url(self):
        self.text = self.url_entry.get()
        self.root.destroy()
        

def validate_link(video_url):
    parsed_url = urlparse(video_url)
    # path: specifies the specific location or resource being accessed
    # netloc: url component that specifies the domain name or ip addess 
    if parsed_url.netloc not in ['www.youtube.com', 'youtube.com', 'm.youtube.com', 'youtu.be']:
        return None
    
    # query: contains the video id
    query_params = parse_qs(parsed_url.query)
    # search for 'list' needs to be first because both can be playing ('v')
    if 'list' in query_params: # check for playlist
        return loop_through_playlist
    
    if 'v' in query_params: # check for video
            return process_file


def loop_through_playlist(playlist_url, output_path, _):
    playlist = Playlist(playlist_url) # an array with all the videos from a playlist 
    def wrapper(video_url): 
        return process_file(video_url, output_path, True) 
    
    with ThreadPoolExecutor() as executor: # ThreadPoolExecutor provides ways to manage multiple threads concurrently
        results = list(executor.map(wrapper, playlist)) # creates a list of concurrent threads


def process_file(video_url, output_path, isPlaylist):
    if isPlaylist:
        # get the specific index from the playlist
        # index = find_playlist_index(video_url)
        pass 
    
    video_name, file_path = download_YouTube_mp4(video_url, output_path)
    wav_file_path = convert_mp4_to_wav(file_path, output_path)
    text = convert_wav_to_text(wav_file_path, output_path)
    write_transcript_to_file(text, video_name, output_path)
    delete_created_files(output_path)


def find_playlist_index(playlist_url):
    parsed_url = urlparse(playlist_url)
    query_params = parse_qs(parsed_url.query)
    index = query_params.get('index', [None])[0]  
    print(index)
    if index is not None:
        return int(index)


def download_YouTube_mp4(video_url, output_path):
    yt = YouTube(video_url, on_progress_callback = on_progress)
    video_stream = yt.streams.get_highest_resolution()
    video_name = yt.title
    output_path = os.path.join(os.getcwd(), output_path)
    file_path = video_stream.download(output_path=output_path)
    return video_name, file_path


def convert_mp4_to_wav(file_path, output_path):
    filename = os.path.splitext(os.path.basename(file_path))[0]
    # mp.VideoFileClip.ffmpeg_binary = r"C:\\Users\\CMP_OwDiBacco\\Downloads\\Convert Youtube URL to Transcript\\ffmpeg-7.1-full_build (1)\\ffmpeg-7.1-full_build\\bin\\ffmpeg.exe" # replace with path to ffmpeg.exe after you set it as a path in your enviormental varaibles
    # ffmpeg is not needed ^
    video = mp.VideoFileClip(file_path)
    output_wav_dir = os.path.join(output_path, "Wav")
    os.makedirs(output_wav_dir, exist_ok=True)
    output_wav_path = os.path.join(output_wav_dir, filename + '.wav')
    video.audio.write_audiofile(output_wav_path)
    return output_wav_path


def convert_wav_to_text(file_path, output_path):
    chunk_text = []
    audio = AudioSegment.from_wav(file_path)
    filename = os.path.splitext(os.path.basename(file_path))[0]
    chunks = split_on_silence(audio, min_silence_len=500, silence_thresh=-50)
    if not chunks:
        return ""  

    recognizer = sr.Recognizer()
    output_path = os.path.join(output_path, "Clips", filename)
    os.makedirs(output_path, exist_ok=True)

    for i, chunk in enumerate(chunks):
        full_wav_path = os.path.join(output_path, f"chunk{i+1}.wav")
        chunk.export(full_wav_path, format="wav")
        
        with sr.AudioFile(full_wav_path) as source:
            audio_chunk = recognizer.record(source, duration=4)
            try:
                text = recognizer.recognize_google(audio_chunk)
                chunk_text.append(text)
            except sr.UnknownValueError:
                print(f"Chunk {i+1}: No Speech Recognized")
            except sr.RequestError as e:
                print(f"Error With Google Speech Recognition API: {e}")
            except Exception as e:
                print(f"An Error Occurred: {e}")

    final_text = ''.join(chunk_text)
    return final_text


def write_transcript_to_file(text, video_name, output_path):
    output_path = os.path.join(os.getcwd(), "txt", output_path) # output text file path
    with open(os.path.join(output_path, video_name + ".txt"), "w") as txt_file:
        txt_file.write(text)


def delete_created_files(delete_path):
    current_directory = os.getcwd()
    output_wav_dir = os.path.join(current_directory, delete_path, "Wav")
    output_clips_dir = os.path.join(current_directory, delete_path, "Clips")
    shutil.rmtree(output_wav_dir)
    shutil.rmtree(output_clips_dir)
    

def get_transcript_from_youtube_url():
    app = App()
    video_url = app.text
    response = validate_link(video_url)
    output_path_id = str(uuid.uuid4())
    output_path = f'output\\{output_path_id}'
    response(video_url, output_path, False)
        
if __name__ == "__main__":
    get_transcript_from_youtube_url() 