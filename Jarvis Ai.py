##from Ai.Text_To_Speech import engine_tts
##
##engine_tts.say("im online and ready sir.", False)
##
##from Ai.Wake_Word import engine_ww
##
##listener_ww = engine_ww.Recognizer()
##listener_ww.start()
##listener_ww.recognize_wake_word()
##listener_ww.stop()
##
from Ai.Speech_To_Text import engine_stt

listener_stt = engine_stt.Recognizer()
listener_stt.silence_threshold = 15

while True:
    print("recording vc...")
    print(listener_stt.listen_recognize())
