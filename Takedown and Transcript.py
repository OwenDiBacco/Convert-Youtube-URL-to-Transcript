import re
import os
import uuid
import shutil
import Create_Notes_From_AI
from pytubefix import YouTube
from pytubefix.cli import on_progress
import tkinter as tk
import moviepy.editor as mp
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

        self.check_var = tk.IntVar()
        self.checkbutton = tk.Checkbutton(self.root, text="AI Response Generation", variable=self.check_var)
        self.checkbutton.pack()

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
    playlists = Playlist(playlist_url) # an array with all the videos from a playlist 
    # the videos are in order in the playlist array
    def wrapper(video_url): 
        index = playlists.index(video_url)
        return process_file(video_url, output_path, index) 
    
    # chunking the array to control the concurrency 
    # tried to chunk array but it doesn't help with anything
    with ThreadPoolExecutor() as executor: # ThreadPoolExecutor provides ways to manage multiple threads concurrently
        list(executor.map(wrapper, playlists)) # creates a list of concurrent threads


def process_file(video_url, output_path, index):    
    video_name, file_path = download_YouTube_mp4(video_url, output_path)
    wav_file_path = convert_mp4_to_wav(file_path, output_path)
    text = convert_wav_to_text(wav_file_path, output_path)
    write_transcript_to_file(text, video_name, output_path, index)
    current_directory = os.getcwd()
    full_wav_path = os.path.join(current_directory, wav_file_path)
    filename = os.path.splitext(os.path.basename(file_path))[0] # gets the file name without
    current_clips_directory = os.path.join(current_directory, output_path, "clips", filename)
    delete_created_files(full_wav_path) # don't delete the entire folder when concurrently processing, instead delete the individual wav file 
    delete_created_directory(current_clips_directory)


def find_playlist_index(playlist_url):
    parsed_url = urlparse(playlist_url)
    query_params = parse_qs(parsed_url.query)
    index = query_params.get('index', [None])[0]  
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
    output_wav_dir = os.path.join(output_path, "wav")
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
    output_path = os.path.join(output_path, "clips", filename)
    os.makedirs(output_path, exist_ok=True)

    for i, chunk in enumerate(chunks):
        full_wav_path = os.path.join(output_path, f"chunk{i+1}.wav")
        chunk.export(full_wav_path, format="wav")
        
        with sr.AudioFile(full_wav_path) as source:
            audio_chunk = recognizer.record(source, duration=4)
            try:
                text = recognizer.recognize_google(audio_chunk) + " "
                chunk_text.append(text)
            except sr.UnknownValueError:
                print(f"Chunk {i+1}: No Speech Recognized")
            except sr.RequestError as e:
                print(f"Error With Google Speech Recognition API: {e}")
            except Exception as e:
                print(f"An Error Occurred: {e}")

    final_text = ''.join(chunk_text)
    return final_text


def write_transcript_to_file(text, video_name, output_path, index):
    output_path = os.path.join(os.getcwd(),  output_path, "txt") # output text file path
    os.makedirs(output_path, exist_ok=True)
    if index != None:
        filename = str(index + 1) + ". " + video_name + ".txt"

    else:
        filename = video_name + ".txt"
    
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)  # Replace invalid characters with nothing
    with open(os.path.join(output_path, filename), "w") as txt_file:
        txt_file.write(text)


def combine_text_files(folder_path, output_file_name): # taken from other application
    def contains_text_files(directory_path):
        total_txt_files = 0
        files = os.listdir(directory_path)
        for file in files:
            if file.lower().endswith('.txt'):
                total_txt_files += 1

        return total_txt_files

    output_file = os.path.join(folder_path, output_file_name + ".txt") 
    if contains_text_files(folder_path) > 1: 
        recorded = []
        with open(output_file, 'w') as outfile:  
            number_of_files = 0
            for file in os.listdir(folder_path): 
                if file.endswith('.txt'): 
                    number_of_files += 1

            file_iterations = -1
            while len(recorded) < number_of_files -1: 
                file_iterations += 1
                if len(str(file_iterations)) < 1: 
                    file_iterations = "0" + file_iterations

                for filename in os.listdir(folder_path): 
                    if filename.endswith(".txt") and str(file_iterations) in filename: 
                        recorded.append(filename) 
                        file_path = os.path.join(folder_path, filename) 
                        filename = os.path.splitext(filename)[0]
                        filename = filename.encode('ascii', 'ignore').decode('ascii') # gets rid of unicode
                        # some Mosh video titles contain unicode
                        with open(file_path, 'r') as infile: 
                            outfile.write(f'Section: {filename}')
                            outfile.write("\n")
                            outfile.write("\n")
                            outfile.write(infile.read())
                            outfile.write("\n")  
                            outfile.write("\n")

        return output_file 
    
    elif contains_text_files(folder_path) == 1:
        files = os.listdir(folder_path)
        for file in files:
            if file.lower().endswith('.txt'):
                full_file_path = os.path.join(folder_path, file) 
                return full_file_path

    else:
        return None 


def write_AI_response(combined_txt_path, output_path):
    content = ''
    with open(combined_txt_path, 'r') as file:
        content = file.read() + " /n" # reads the content from the combined text file

    with open('prompt.txt', 'r') as file: # prompt.txt copied from other program
        content += file.read()

    response = Create_Notes_From_AI.prompt_genai(content) 
    ai_response_folder = os.path.join(os.getcwd(), output_path, "ai script") 
    os.makedirs(ai_response_folder) 
    ai_response_file = os.path.join(ai_response_folder, "ai script.txt") # defines a variable for the AI generated workseet path

    f = open(ai_response_file, "w") # creates and opens new txt file
    f.write(response) # writes the AI response to the worksheet
    f.close()


def delete_created_files(delete_path):
    os.remove(delete_path)
    # os.remove(): delete an individual file 
    # shutil.rmtree(): deletes the root node and all nodes below it


def delete_created_directory(delete_path):
    shutil.rmtree(delete_path)


def get_transcript_from_youtube_url():
    app = App()
    video_url = app.text
    response = validate_link(video_url)
    output_path_id = str(uuid.uuid4())
    output_path = f'output\\{output_path_id}'
    response(video_url, output_path, None)
    wav_directory = os.path.join(os.getcwd(), output_path, "wav")
    clips_directory = os.path.join(os.getcwd(), output_path, "clips")
    txt_directory = os.path.join(os.getcwd(), output_path, "txt")
    delete_created_directory(wav_directory)
    delete_created_directory(clips_directory)
    combined_text_file = combine_text_files(txt_directory, "all") # combined text file will be the only txt file if there is only one 
    
    if combined_text_file != None and app.check_var.get() == 1: 
        write_AI_response(combined_text_file, output_path)

    # breaks at the end of the program; the same thing happened in the other program
    # somtimes happens and somtimes doesn't
    # ?????

if __name__ == "__main__":
    get_transcript_from_youtube_url() 