README

Student Name:
Michael Cunningham

Student Number:
21362621


# 🏎️ 🏁 F1 RCC - Formula One Real-Time Comms Cleaner 🏎️ 🏁
This project detects speech in Formula 1 race communications, reduces engine noises, and trancribes in real-time using Voicde Activity Detection (VAD) and OpenAI Whisper Medium


## 📂 Data Used

The audio used in this project was sourced from:  
🔗 https://www.youtube.com/watch?v=IBnixyOK8uQ

It was downloaded as an `.mp3`, converted to `.wav`, and is located at:
Audio/F1_AUDIO.wav 

### 🎥 Project Report (VIDEO FORMAT): 
The project report is in video format MP4 due to the real-time app demonstration.
**Filename:** `Final Project Report.mp4`
**Location:** Root folder of this submission. 

### Environment Setup & Dependencies 🤓
### Required Base Software 
- Python 3.10 or higher
- `ffmpeg` must be installed in your system `PATH` for whisper. 

### Creating a Virtual Environment: 
```bash
python -m venv venv
source venv/bin/activate         # Mac/Linux
venv\Scripts\activate            # Windows
```

### Installing Necessary Dependencies 
pip install -r requirements.txt


### Running Jupyter Notebook 📙
- Open Terminal/CommandLine 
- CD to the Speech&Audio Folder (This folder)
- Run the command:
```bash
pip install -r requirements.txt
```
- Run the command: 
```bash
`jupyter notebook`
```

### Running the Application 
- Open a Terminal/CommandLine Window
- CD to the root folder (Speech&Audio) (This folder)
- Run the command:
```bash
pip install -r requirements.txt
```
- Then CD to F1_COMMS_APP
- Run the command:
```bash
pip python3 f1_comms_app.py
```
OR
```bash
pip python f1_comms_app.py
```

### Simulation Technique
Currently the simulation has this commented out: 
```bash         
        # Time Sleep enables the race audio to appear live. 
        # time.sleep(chunk_size)
```
This allows the system to quickly process the audio, and skips chunks that do not have any voice activity detected in them.
If you wish to simulate a real time race, simply uncomment this, the program will run for 20 minutes (lenght of audio file), it has been commented out just so you can get an understanding quickly of the system working. 


### Folder Structure 
- Audio /                   (Contains input audio files)
- Transcriptions/           (Contains the transcripted text output by the system)
- whisper-transcription     (Used to store temporary generated audio chunks for transcription)
- Recorded-Audio            (Clipped audio containing just the recorded audio segments.)
- F1_COMMS_APP/             (GUI App)
- Speech&Audio_FYP.ipynb    (Notebook Version for demonstration purposes)
- requirements.txt          (All of the dependencies required by the system)
- README.md                 (This file.)