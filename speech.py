import deepspeech
import wave
from pydub import AudioSegment
import numpy as np

# 定义语音文件路径
# mp3 转换 wav
audio_path = 'audio/test-chinese.wav'
if(audio_path.endswith(".mp3")):
    wav_audio = AudioSegment.from_file(audio_path, format='mp3').set_frame_rate(16000).set_channels(1).set_sample_width(2)
    wav_audio.export('audio/test-chinese.wav', format='wav')
    audio_path = 'audio/test-chinese.wav'

# 加载 DeepSpeech 模型
model_path = 'DeepSpeech/deepspeech-0.9.3-models.pbmm'
beam_width = 500
model = deepspeech.Model(model_path)
model.beamWidth = beam_width

# 加载语音文件
with wave.open(audio_path, 'rb') as audio_file:
    audio_data = np.frombuffer(audio_file.readframes(audio_file.getnframes()), np.int16)

# 将语音转换成文本
text = model.stt(audio_data)
print("识别结果：", text)
