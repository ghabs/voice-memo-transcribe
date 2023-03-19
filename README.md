## Voice Memo Transcribe

#### Transcribe Apple Voice Memos

Transcribe apple voice memos and add annotations from an LLM call.

#### Installation
create a virtual environment and install the requirements.txt (I'll eventually get around to making a executable)

#### Commands

GUI
```
python main.py
```

Command Line Transcribe
```
python main.py --check-directory 
```

The settings are stored in config.yaml / are set by the GUI. To use the OpenAI LLM call you'll need to set your api token.

Index.txt is used as a key value store for the names of the files so that it only transcribes the memo once. If you want to retranscribe it, you can remove that file name from index.txt.

Some nice to have's not yet implemented:
- More Command Line Options
- Rename the file transcripts based on their contents
