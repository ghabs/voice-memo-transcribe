from llm import LLMFormatter
from transcriber import Transcriber
import os
import tkinter as tk
from tkinter import filedialog
from tkinter.simpledialog import Dialog
import subprocess
from tkinter import ttk
import yaml
import threading

from dotenv import load_dotenv
load_dotenv()


# Open the YAML file for reading
with open('user_config.yaml', 'r') as file:
    # Load the contents of the file into a dictionary
    config = yaml.safe_load(file)

transcripts_dir = os.path.expanduser(config['TRANSCRIPTS_DIR'])
default_prompt = config['DEFAULT_PROMPT']
os.environ['OPENAI_API_KEY'] = config['OPENAI_API_KEY']
MODEL_SIZE = config['OPENAI_MODEL_SIZE']

MODEL_SIZES = ["tiny.en", "base.en", "small.en", "medium.en", "large"]


def read_index_pairs(file_path):
    key_value_pairs = {}
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line:
                key, value = line.split("=")
                key_value_pairs[key.strip()] = value.strip()
    return key_value_pairs


def transcribe_file(file_name):
    # Do something with the file name
    print("Transcribing file: " + file_name)
    return file_name


def save_transcript(file_name, transcript, llm_transcript):
    # Do something with the transcript
    print("Saving transcript: " + transcript)
    file_name = os.path.splitext(file_name)[0]
    with open(os.path.join(transcripts_dir, file_name + ".md"), "w") as file:
        file.write("## Transcript\n")
        file.write(transcript)
        file.write("\n\n")
        file.write("## LLM\n")
        file.write(llm_transcript)
    return os.path.join(transcripts_dir, file_name + ".md")


llm_formatter = LLMFormatter(
    oa_key=os.environ['OPENAI_API_KEY'], workflow=default_prompt)


def open_folder():
    subprocess.call(['open', transcripts_dir])


class SettingsWindow(Dialog):
    def body(self, master):
        api_label = ttk.Label(master, text="OpenAI API Key:")
        api_label.pack()
        self.api_key_entry = ttk.Entry(master)
        self.api_key_entry.pack()
        self.api_key_entry.insert(0, os.environ['OPENAI_API_KEY'])
        browse_folder_button = tk.Button(
            master, text="Select Transcript Folder", command=self.browse_folder)
        browse_folder_button.pack(pady=10)
        model_size_label = ttk.Label(master, text="Model Size:")
        model_size_label.pack()
        self.model_size = ttk.Combobox(
            master, values=["tiny", "base", "small", "medium", "large"])
        self.model_size.current(MODEL_SIZE)
        self.model_size.pack()
        prompt_text_label = ttk.Label(
            master, text="LLM Prompt (run after transcription):")
        prompt_text_label.pack()
        self.prompt_text = tk.Text(master, height=10, width=50, wrap=tk.WORD)
        self.prompt_text.insert(tk.END, default_prompt)
        self.prompt_text.pack(padx=10, pady=(0, 10))
        self.results = None

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'r') as file:
                file_contents = file.read()
                self.prompt_text.delete(1.0, tk.END)
                self.prompt_text.insert(tk.END, file_contents)
                global default_prompt
                default_prompt = file_contents

    def browse_folder(self):
        documents_folder = os.path.expanduser('~/Documents')
        folder_path = filedialog.askdirectory(initialdir=documents_folder)
        global transcripts_dir
        transcripts_dir = folder_path

    def validate(self) -> bool:
        self.results = {'api_key': self.api_key_entry.get(), 'prompt_text': self.prompt_text.get(
            1.0, tk.END), 'model_size': self.model_size.current()}
        return super().validate()


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Voice Memo Transcriber")
        self.geometry("250x200")

        f = ttk.Frame()

        run_button = tk.Button(
            f, text="Transcribe Voice Memos", command=self.run_function, anchor='n')
        run_button.pack()

        f.pack(expand=True, padx=10, pady=10)

        sf = ttk.Frame()
        toggle_button = tk.Button(
            sf, text="Options", command=self.call_settings, anchor='n')
        toggle_button.pack(side="left")

        show_button = tk.Button(
            sf, text="Show Transcripts", command=open_folder, anchor='n')
        show_button.pack(side="left")

        sf.pack(expand=True, padx=10, pady=10)

        pf = ttk.Frame()
        pf.pack(fill='both', expand=True, padx=10, pady=10)

        self.progress_label = tk.Label(pf, text="", wraplength=300)
        self.progress_label.pack()

        self.thread = None
        self.model_type = MODEL_SIZES[config['OPENAI_MODEL_SIZE']]
        self.transcriber = Transcriber(self.model_type)
        self.llm_formatter = LLMFormatter(
            oa_key=os.environ['OPENAI_API_KEY'], workflow=default_prompt)

    def save_options(self, results):
        config["DEFAULT_PROMPT"] = results['prompt_text']
        global default_prompt
        default_prompt = results['prompt_text'].strip()
        os.environ["OPENAI_API_KEY"] = results['api_key']
        config["TRANSCRIPTS_DIR"] = transcripts_dir
        config["OPENAI_API_KEY"] = results['api_key']
        config["OPENAI_MODEL_SIZE"] = results['model_size']
        MODEL_SIZE = results['model_size']
        if self.model_type != MODEL_SIZES[config['OPENAI_MODEL_SIZE']]:
            self.model_type = MODEL_SIZES[config['OPENAI_MODEL_SIZE']]
            self.transcriber = Transcriber(self.model_type)
        self.llm_formatter = LLMFormatter(oa_key=os.environ['OPENAI_API_KEY'], workflow=default_prompt)
        with open('user_config.yaml', 'w') as file:
            yaml.dump(config, file)

    def call_settings(self):
        w = SettingsWindow(self)
        if w.results is not None:
            self.save_options(w.results)

    def check_new_voice_memos(self):
        pass

    def check_directory(self, transcriber, llm_formatter):
        # Get the list of existing transcripted files
        index_file = config["VOICE_MEMO_INDEX_FILE"]
        files = read_index_pairs(index_file)

        # Get the current list of voice memo files in the directory
        current_files = [f for f in os.listdir(os.path.expanduser(
            config["VOICE_MEMO_LOCATION"])) if f.endswith(".m4a")]
        results = 0
        with open(index_file, "a") as ifile:
            for file in current_files:
                print(file)
                if file not in files:
                    try:
                        # transcribe the voice memo
                        transcript = transcriber.transcribe(os.path.join(
                            os.path.expanduser(config["VOICE_MEMO_LOCATION"]), file))
                        # format the transcript
                        llm_transcript = llm_formatter.format(transcript)
                        # save the transcript
                        transcript_loc = save_transcript(
                            file, transcript, llm_transcript)
                        files[file] = transcript_loc
                        ifile.write(f"{file}={files[file]}\n")
                        results += 1
                    except Exception as e:
                        print(e)
        self.progress_label.config(text=f"Transcribed {results} voice memos.")

    def run_function(self):
        self.progress_label.config(text="Transcribing voice memos...")
        self.thread = threading.Thread(target=self.check_directory, args=(
            self.transcriber, self.llm_formatter))
        self.thread.start()


if __name__ == "__main__":
    gui = GUI()
    gui.mainloop()
