# Re-Dublüman

This project was born out of my desire to make the vocals in the songs of the famous Turkish music group Dedublüman more audible. My goal is to make the vocals in the songs more clearly heard. For this reason, I named the project 'Re-Dublüman'

### About Project
Re-Dublüman is a tool that separates vocals and other instruments in music tracks. This tool uses a sound separation model called Demucs to separate the audio sources, and then allows you to make separate volume adjustments for vocals and other sounds. The project is hosted on [Streamlit](https://re-dubluman.streamlit.app), enabling users to upload audio files and process them instantly

To run this project, follow the steps below:

### 1. **Clone the Repository**

First, clone the repository to your local machine:

```bash
git clone https://github.com/your-username/re-dubluman.git
cd re-dubluman
```

### 2. **Install Dependencies**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### 3. **Run the Streamlit App**
```bash
streamlit run re-dubluman.py
```
### 4. **Upload Your Audio**
In the Streamlit app, you can upload an audio file in MP3 or WAV format, adjust the vocal and other elements' gain, and listen to the processed output.

