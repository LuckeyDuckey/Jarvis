import os
import json
import torch
import numpy as np
import soundfile as sf
import simpleaudio as sa
from tqdm.notebook import tqdm
from os.path import exists, join, basename, splitext

from .tacotron2.hparams import create_hparams
from .tacotron2.model import Tacotron2
from .tacotron2.layers import TacotronSTFT
from .tacotron2.audio_processing import griffin_lim
from .tacotron2.text.__init__ import text_to_sequence
from .hifigan.env import AttrDict
from .hifigan.meldataset import MAX_WAV_VALUE
from .hifigan.models import Generator

print("Setting up, please wait.\n")

with tqdm(total=5, leave=False) as pbar:

    directory = os.path.dirname(os.path.realpath(__file__)) + "\\"
    thisdict = {}
    
    for line in reversed((open(directory + "merged.dict.txt", "r").read()).splitlines()):
        thisdict[(line.split(" ",1))[0]] = (line.split(" ",1))[1].strip()

    def ARPA(text, punctuation=r"!?,.;", EOS_Token=True):
        
        out = ""
        
        for word_ in text.split(" "):
            
            word=word_; end_chars = ""
            
            while any(elem in word for elem in punctuation) and len(word) > 1:
                
                if word[-1] in punctuation: end_chars = word[-1] + end_chars; word = word[:-1]
                else: break
                
            try:
                word_arpa = thisdict[word.upper()]
                word = "{" + str(word_arpa) + "}"
                
            except KeyError:
                pass
            
            out = (out + " " + word + end_chars).strip()
            
        if EOS_Token and out[-1] != ";": out += ";"
        
        return out

    def get_hifigan():
        
        conf = os.path.join(directory + "hifigan", "config_v1.json")
        
        with open(conf) as f:
            json_config = json.loads(f.read())
            
        h = AttrDict(json_config)
        torch.manual_seed(h.seed)
        hifigan = Generator(h).to(torch.device("cuda"))
        state_dict_g = torch.load(directory + "hifimodel", map_location=torch.device("cuda"))
        
        hifigan.load_state_dict(state_dict_g["generator"])
        hifigan.eval()
        hifigan.remove_weight_norm()
        
        return hifigan, h

    hifigan, h = get_hifigan()

    def get_Tactron2():
        
        hparams = create_hparams()
        hparams.sampling_rate = 22050
        hparams.max_decoder_steps = 3000
        hparams.gate_threshold = 0.25
        
        model = Tacotron2(hparams)
        state_dict = torch.load(directory + "MLPTTS")["state_dict"]
        model.load_state_dict(state_dict)
        _ = model.cuda().eval().half()
        
        return model, hparams

    model, hparams = get_Tactron2()

    # Extra Info
    def end_to_end_infer(text, pronounciation_dictionary):
        
        for i in [x for x in text.split("\n") if len(x)]:
            
            if not pronounciation_dictionary:
                if i[-1] != ";":
                    i=i+";"     
            else:
                i = ARPA(i)
                
            with torch.no_grad():
                
                sequence = np.array(text_to_sequence(i, ["english_cleaners"]))[None, :]
                sequence = torch.autograd.Variable(torch.from_numpy(sequence)).cuda().long()
                
                mel_outputs, mel_outputs_postnet, _, alignments = model.inference(sequence)
                y_g_hat = hifigan(mel_outputs_postnet.float())
                
                audio = y_g_hat.squeeze()
                audio = audio * MAX_WAV_VALUE
                
                sf.write(directory + "audio.wav", (audio.cpu().numpy().astype("int16")), hparams.sampling_rate)

pronounciation_dictionary = False
model.decoder.max_decoder_steps = 1000
stop_threshold =  0.9
model.decoder.gate_threshold = stop_threshold

def say(text, run_and_wait):
    
    global pronounciation_dictionary
    
    try:
        end_to_end_infer(text, pronounciation_dictionary)
        play_object = sa.WaveObject.from_wave_file(directory + "audio.wav").play()
        if run_and_wait: play_object.wait_done()
        
    except:
        print("ERROR: TTS failed at unknown point.")
