import whisper
from pydub import AudioSegment 
import math
import json
import sys
import wave
import tqdm

def read_wav(path):
    with wave.open(path, "rb") as wav:
        nchannels, sampwidth, framerate, nframes, _, _ = wav.getparams()
        #print(wav.getparams(), "\nBits per sample =", sampwidth * 8)

        signed = sampwidth > 1  # 8 bit wavs are unsigned
        byteorder = sys.byteorder  # wave module uses sys.byteorder for bytes

        values = []  # e.g. for stereo, values[i] = [left_val, right_val]
        for _ in range(nframes):
            frame = wav.readframes(1)  # read next frame
            channel_vals = []  # mono has 1 channel, stereo 2, etc.
            for channel in range(nchannels):
                as_bytes = frame[channel * sampwidth: (channel + 1) * sampwidth]
                as_int = int.from_bytes(as_bytes, byteorder, signed=signed)
                channel_vals.append(as_int)
            values.append(channel_vals)

    return values, framerate
def Reformat_wav(wav_data):
    output = []
    for sample in wav_data:
        output.append(sample[0])
    return output

SoundFile = "InputAudio/charsarg2.mp3"
InputAudio = AudioSegment.from_mp3(SoundFile)
#from whisper.tokenizer import Tokenizer, get_tokenizer



print('loading model')
#t = get_tokenizer(False)
model = whisper.load_model("tiny")
print('transcribing')
result = model.transcribe(SoundFile,word_timestamps=True)
print('DOING OTHER STUFF')
#print(result)
data = {}
previousWord = ""
roundPresicion = 20
PreviousWordEnd = 0
PartialVoiceI = 0
PreviousI = 0
for segment in result['segments']:
    #print(segment)
    #PreviousWordStart = 0
    for word in tqdm.tqdm(segment["words"]):
        time = word['end'] - word['start']
        print(start,end)
        start = (math.floor(word["start"]*roundPresicion)/roundPresicion)*1000
        end = (math.ceil(word["end"]*roundPresicion)/roundPresicion)*1000
        AudioSnippet = InputAudio[start: end]
        WordWithoutPunct = word["word"]
        for punct in list(".,'!? "):
            if punct in WordWithoutPunct:
                WordWithoutPunct = "".join(WordWithoutPunct.split(punct))
        #AudioSnippet.export(f"VoiceSamples/{WordWithoutPunct}.mp3", format="mp3")
        if not WordWithoutPunct in data:
            data[WordWithoutPunct] = []
        WordData = {}
        WordData["nextWord"] = ""
        WordData['time'] = time
        WordData['previousWord'] = previousWord
        WordData['WordDelay'] = word['start']-PreviousWordEnd
        PreviousWordEnd = word['end']
        #WordData['audio'] = AudioSnippet

        AudioSnippet.export("temp/AudioSnippet.wav", format="wav")
        WordData['audio'] = Reformat_wav(read_wav("temp/AudioSnippet.wav")[0])
        WordData['pitch'] = None
        WordData['volume'] = None
        WordData['speed'] = None
        data[WordWithoutPunct].append(WordData)
        if previousWord in data:
            data[previousWord][PreviousI]["nextWord"] = WordWithoutPunct
        PreviousI = len(data[WordWithoutPunct])-1
        previousWord = WordWithoutPunct
    if PartialVoiceI % 5 == 0:
        with open(f'PartialVoice_{PartialVoiceI}.CuppaVoice','w') as file:
            #pass
            file.write(json.dumps(data,indent=4))
    PartialVoiceI += 1
with open('FullVoice.CuppaVoice','w') as file:
    file.write(json.dumps(data,indent=4))
    #print(''.join(f"{word['word']}[{word['start']}/{word['end']}]" 
     #               for word in segment['words']))
#print(result["text"])
