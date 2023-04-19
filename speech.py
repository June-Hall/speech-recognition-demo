import deepspeech
import numpy as np
import sounddevice as sd

# 初始化 DeepSpeech 模型
model_path = 'DeepSpeech/deepspeech-0.9.3-models.pbmm'  # 模型文件路径
beam_width = 500
model = deepspeech.Model(model_path)
model.setBeamWidth(beam_width)

# 录制音频并进行识别
duration = 5  # 录制时长（秒）
sample_rate = 16000  # 采样率
channels = 1  # 音频通道数

# 录制音频的回调函数
def audio_callback(indata, frames, time, status):
    audio_data.append(indata.copy())

# 创建录音缓冲区
audio_data = []

# 录制音频
with sd.InputStream(samplerate=sample_rate, channels=channels, callback=audio_callback):
    print("开始录音...")
    sd.sleep(duration * 1000)
    print("录音完成.")

# 将录音数据转换为 numpy 数组
audio_data = np.concatenate(audio_data)
audio_data = np.ravel(audio_data)
audio_data = (audio_data * 32767).astype(np.int16)

# 语音识别
text = model.stt(audio_data)
print("识别结果：", text)
