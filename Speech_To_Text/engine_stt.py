import speech_recognition as sr
import pyaudio
import wave
import os
import audioop

class Recognizer:
    def __init__(self):
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024
        self.silence_threshold = 20
        self.silence_duration = 20
        self.audio_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "audio.wav")
        self.stt = sr.Recognizer()

        # First inference is always longest
        with sr.AudioFile(self.audio_file[:-9]+"load_audio.wav") as source:
            audio = self.stt.record(source)
            try: self.stt.recognize_whisper(audio, language="english", model="base.en")
            except: pass

    def adjust_for_ambient_noise(self, duration):
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)

        silence_mean = []

        for i in range(0, int(self.rate / self.chunk * duration)):
            data = stream.read(self.chunk)
            rms = audioop.rms(data, 2)
            silence_mean.append(rms)

        self.silence_threshold = sum(silence_mean) / len(silence_mean) - 10

        stream.stop_stream()
        stream.close()
        p.terminate()

    def listen_recognize(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)

        frames = []
        silence_mean = [0*self.silence_duration]

        for i in range(0, int(self.rate / self.chunk * 1)):
            data = stream.read(self.chunk)
            frames.append(data)
            
            rms = audioop.rms(data, 2)
            silence_mean.append(rms)
            silence_mean.pop(0)

        while True:
            data = stream.read(self.chunk)
            frames.append(data)

            rms = audioop.rms(data, 2)

            silence_mean.append(rms)
            silence_mean.pop(0)

            #print(sum(silence_mean) / len(silence_mean))

            if sum(silence_mean) / len(silence_mean) < self.silence_threshold:
                break

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(self.audio_file, "wb")
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b"".join(frames))
        wf.close()
        
        with sr.AudioFile(self.audio_file) as source:
            audio = self.stt.record(source)

        try: text = self.stt.recognize_whisper(audio, language="english", model="base.en")
        except: text = None
            
        return text
