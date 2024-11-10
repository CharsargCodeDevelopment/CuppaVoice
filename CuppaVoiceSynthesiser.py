import json
from difflib import SequenceMatcher
import wave
import tkinter as tk
from tkinter import filedialog, messagebox


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def Synthesise(text, VoiceFile, OutputFile):
    TextToSynthesise = []
    Words = []
    for word in text.split(" "):
        WordList = []
        for punct in list(".,!';:?"):
            word = "".join(word.split(punct))
        Words.append(word)
        for letter in list(word):
            WordList.append(ord(letter))
        TextToSynthesise.append(WordList)

    with open(VoiceFile) as f:
        data = json.load(f)

    i = 0
    previousWord = ""
    WordIndexes = []
    for word in Words:
        WordToSynthesise = TextToSynthesise[i]
        WordBiases = []
        AllBiases = []
        for SynthWord in data:
            NumberWord = []
            for letter in list(SynthWord):
                NumberWord.append(ord(letter))
            bias = similar(SynthWord, word)
            AllBiases.append(bias)
            WordBiases.append([bias, SynthWord])
        for SynthWord in WordBiases:
            if SynthWord[0] == max(AllBiases):
                WordIndexes.append(SynthWord[1])
                break
        i += 1

    print(WordIndexes)
    AudioIndexes = []
    previousWord = ""
    i = 0
    nextWord = ""
    for WordIndex in WordIndexes:
        AudioVariations = data[WordIndex]
        AudioVariationBiases = []
        if i < len(WordIndexes) - 1:
            print(i)
            nextWord = WordIndexes[i + 1]
        for AudioVariation in AudioVariations:
            bias = min(1, similar(previousWord, AudioVariation["previousWord"]) + 0.2)
            if i != len(WordIndexes):
                bias *= min(1, similar(nextWord, AudioVariation["nextWord"]) + 0.2)
            AudioVariationBiases.append(bias)
        j = 0
        for bias in AudioVariationBiases:
            if bias == max(AudioVariationBiases):
                AudioIndexes.append(j)
                break
            j += 1
        previousWord = Words[i]
        i += 1

    print(AudioIndexes)
    sound = []
    i = 0
    samplerate = 44100
    for WordIndex in WordIndexes:
        index = min(AudioIndexes[i], len(data[WordIndex]) - 1)
        AudioVariation = data[WordIndex][index]
        VoiceSample = AudioVariation["audio"]
        print(AudioVariation["WordDelay"])
        for _ in range(int(samplerate * AudioVariation["WordDelay"])):
            sound.append(int(255 / 2))
        for sample in VoiceSample:
            sound.append(sample)
        print(min(sound), max(sound))
        i += 1

    MaxSound = max(abs(min(sound)), max(sound))
    for i in range(len(sound)):
        sound[i] = int((((sound[i] / (MaxSound * 2)) + 1) / 2) * 255)
    print(min(sound), max(sound))
    with wave.open(OutputFile, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(1)
        wav_file.setframerate(samplerate)
        wav_file.writeframes(bytes(sound))


def CorrectInputTextToWorkWithModel(text, changefile):
    with open(changefile) as file:
        ChangeData = file.read().split("\n")
    for Changer in ChangeData:
        print(Changer)
        inputWord, outputWord = Changer.split(':')
        text = outputWord.join(text.split(inputWord))
    return text


def browse_voice_file():
    filename = filedialog.askopenfilename(filetypes=[("CuppaVoice Files", "*.CuppaVoice"), ("All Files", "*.*")])
    voice_file_var.set(filename)


def synthesize_text():
    text = text_entry.get("1.0", tk.END).strip()
    voice_file = voice_file_var.get()
    if not text or not voice_file:
        messagebox.showwarning("Input Error", "Please provide both text and a CuppaVoice file.")
        return

    output_file = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV Files", "*.wav"), ("All Files", "*.*")])
    if not output_file:
        return

    try:
        Synthesise(text, voice_file, output_file)
        messagebox.showinfo("Success", f"Audio synthesized successfully and saved to {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# Setting up the GUI
root = tk.Tk()
root.title("Text to Speech Synthesizer")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=10, pady=10)

text_label = tk.Label(frame, text="Enter text:")
text_label.grid(row=0, column=0, sticky="w")

text_entry = tk.Text(frame, wrap=tk.WORD, width=50, height=10)
text_entry.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

voice_file_label = tk.Label(frame, text="Select CuppaVoice file:")
voice_file_label.grid(row=2, column=0, sticky="w")

voice_file_var = tk.StringVar()
voice_file_entry = tk.Entry(frame, textvariable=voice_file_var, width=40)
voice_file_entry.grid(row=3, column=0, padx=5, pady=5)

browse_button = tk.Button(frame, text="Browse", command=browse_voice_file)
browse_button.grid(row=3, column=1, padx=5, pady=5)

synthesize_button = tk.Button(frame, text="Synthesize", command=synthesize_text)
synthesize_button.grid(row=4, column=0, columnspan=3, pady=10)

root.mainloop()
