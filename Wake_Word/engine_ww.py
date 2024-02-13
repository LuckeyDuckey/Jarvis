import os
import time
import pyaudio
import threading
import librosa
import numpy as np
import tensorflow as tf
from collections import deque
from tensorflow.keras.models import load_model

class Recognizer(threading.Thread):
    def __init__(self):
        super(Recognizer, self).__init__()
        self.chunk_size = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 22050
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk_size)
        self.queue = deque(maxlen=int(2 * self.rate / self.chunk_size))
        self.running = True
        self.model = load_model(os.path.dirname(os.path.realpath(__file__)) + "\\WWD.h5")
    
    def run(self):
        while self.running:
            data = self.stream.read(self.chunk_size)
            self.queue.put(data)
    
    def stop(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
    
    def recognize_wake_word(self):
        audio_data = np.frombuffer(b''.join(self.queue), dtype=np.int16)
        audio_data = librosa.util.buf_to_float(audio_data)
        mel_spectrogram = librosa.feature.melspectrogram(y=audio_data, sr=22050, n_mels=256, hop_length=128, fmax=8000)
        out = librosa.power_to_db(mel_spectrogram, ref=np.max)
        
        audio = np.array(out)
        audio = audio.reshape(1,audio.shape[0],audio.shape[1],1)
        prediction = self.model.predict(audio, verbose=0)

        return True if prediction[0][1] >= 0.9 else False
