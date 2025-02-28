# YouTube Video Transcript Generator

## Table of Contents

- [Objective](#Objective)
- [Installations](#Installations)
- [Running-The-Application](#Running-The-Application)
- [How-The-Application-Works](#How-The-Application-Works)

## Objective
The objective of this program is to receive a URL to a YouTube video or a Youtube playlist and generate a transcript for each video.

## Installations
1. Clone the Repository
  a. Go to your intended directory in your Command Prompt
```bash
cd Downloads/[Your Directory]
```
    
  b. Paste this command:
```bash
git clone https://github.com/OwenDiBacco/Convert-YouTube-URL-To-Transcript.git
```
     
2. Make The Required pip Installations <br/>
```bash
pip install -r requirements.txt
```

3. Get a Gemini API Key

   a). click on this link: https://aistudio.google.com/<br>
   b). click on 'get api key' button, then the 'create api key' button<br>
   c). select the Google Cloud Console project you would like this key associated with<br>
   d). then select 'create api key in existing project'<br>
   e). copy this key now; this is the only time you'll be able to access it<br>
   d). create a file named '.env,' declare a variable named 'API_KEY' and store your API key value here. This creates an environement variable named 'API KEY'<br>

4. Obtain poToken and visitorData (2/20/2025 Bot Detection Bypass Solution)

A Proof-of-Origin Token, or a PO Token, is a token required by YouTube, that acts as an identifier and is to be passed along with a request in conjunction with the visitor data, which allows authorization for guest users. 

  a). Go into an incognito / guest tab in your web provider<br>
  b). Click this YouTube Embedded link: https://www.youtube.com/embed/aqz-KE-bpKQ<br>
  c). Filter by: v1/player<br>
  d). Click the video and check the network tab<br>
  e). In the request payload, find the Po Token at the poToken key<br>
        This key will be located under the serviceIntegrityDimensions element<br>
  f). Find the visitorData key and save the value<br>
        This will be located under: context => tvAppInfo<br>
  g). When the application is first run, you will be prompted to enter both these keys<br>
        Note: you will only be prompted to enter this information once<br>


## Running-The-Application

1. run the Takedown and Transcript.pu module
2. paste a link to either a YouTube video or playlist in the text box
3. optionally, select the check box that will allow you to create an AI-generated worksheet representing the material

## How-The-Application-Works

1. The validate_link() function first makes sure the user input a valid https link. Then the function determines whether the link directs you to a YouTube video or a YouTube playlist and returns the function that corresponds to either.<br>
2. The loop_through_playlist() function creates a thread for each video in the playlist and passes each video into the process_file() function.<br>
3. The process_file() function first downloads the video as an mp4 file, which is then converted to a wav file, to be transcripted and written to a text file.<br>
4. Once all the videos are processed, a text file which contains the transcrpts of each created text file is used in the prompt to the AI service.<br>
5. The write_AI_response() function uses the combined text file and the prompt.txt file which contains the prompt for the AI service to generate a response from the prompt_genai() funtion in the Create_Notes_From_AI module.<br>
6. The prompt_genai() function uses the 'API_KEY' environment variable to generate a response from Gemini AI service, which is written to a text file.<br>
