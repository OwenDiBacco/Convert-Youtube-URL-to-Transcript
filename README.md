# YouTube Video Transcript Generator

## Objective
The objective of this program is to receive a URL to a YouTube video and produce a text transcript of the audio.

## Installations
1. Clone the Repository
  a. Go to your intended directory in your Command Prompt
    ```bash
    cd Downloads/[Your Directory]`
    ```
    
  b. Paste this command:
     ```bash
     git clone https://github.com/OwenDiBacco/Convert-YouTube-URL-To-Transcript.git
     ```
     
2. Make The Required pip Installations
   a. In the terminal of the “Takedown and Transcript.py” file, paste these installations: “pip install pytubefix moviepy SpeechRecognition pydub”

## Running The Application

1. The only requirement to run the application is to place your YouTube video url as the ‘video_url’ parameter in the ‘get_transcript_from_youtube_url’ function.
```py
get_transcript_from_youtube_url(video_url = "")
```

  
