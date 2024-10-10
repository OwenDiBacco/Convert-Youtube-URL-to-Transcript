import os
import uuid
from pytubefix import YouTube
from pytubefix.cli import on_progress
import moviepy.editor as mp
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pathlib import Path

def download_YouTube_mp4(video_url):
    yt = YouTube(video_url, on_progress_callback = on_progress)
    video_stream = yt.streams.get_highest_resolution()
    file_path = video_stream.download()
    return file_path


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


def delete_individual_variables(arr):
    for a in arr:
        del a


def delete_created_files(workspace, output_path):
    delete_script_path = os.path.join(workspace, 'Delete.py')
    with open(delete_script_path, "w") as wrfile:
        wrfile.write('import shutil\n')
        wrfile.write(f'shutil.rmtree(r"{output_path}")\n')
        wrfile.write('import os\n')
        wrfile.write(f'os.remove(r"{delete_script_path}")\n')

    os.system(f'python3 "{delete_script_path}"')


def get_transcript_from_youtube_url(video_url='https://www.youtube.com/watch?v=pTB0EiLXUC8'):
    output_path_id = str(uuid.uuid4())
    output_path = f'.\\{output_path_id}'
    current_dir = Path.cwd()
    delete_dir = os.path.join(current_dir, output_path_id)
    file_path = download_YouTube_mp4(video_url)
    wav_file_path = convert_mp4_to_wav(file_path, output_path)
    text = convert_wav_to_text(wav_file_path, output_path)
    delete_individual_variables([file_path, wav_file_path, output_path])
    delete_created_files(current_dir, delete_dir)


if __name__ == "__main__":
    get_transcript_from_youtube_url() 