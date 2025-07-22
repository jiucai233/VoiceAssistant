"""
Speech-to-Text (STT) Module - Based on OpenAI Whisper
Voice to text conversion module

Input: Audio file path (string) or audio byte data (bytes)
Output: Transcribed text result (string)
"""

import whisper
import sounddevice as sd
import os
from scipy.io.wavfile import write
from typing import Union, Optional


class STTModule:
    def __init__(self, model_size: str = "small"):
        """
        Initialize STT module
        
        Input parameters:
        - model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
        """
        self.model = whisper.load_model(model_size)
        
    def transcribe_from_file(self, audio_file_path: str, language: str = "ko") -> str:
        """
        Transcribe text from audio file - Based on original STTdemo code
        
        Input:
        - audio_file_path: Audio file path (string, supports .wav, .mp3, .m4a etc.)
        - language: Language recognition code (string, e.g. "ko" Korean, "zh" Chinese, "en" English)
        
        Output:
        - Transcribed text content (string)
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        try:
            result = self.model.transcribe(audio_file_path, language=language)
            return result["text"]
        except Exception as e:
            print(f"STT transcription error: {e}")
            return ""
    
    def record_and_transcribe(self, duration: int = 5, sample_rate: int = 16000, 
                             language: str = "ko", output_file: str = "recorded.wav") -> str:
        """
        Record and transcribe
        
        Input:
        - duration: Recording duration (seconds) (int)
        - sample_rate: Sample rate (int, default 16000Hz)
        - language: Language recognition code (string)
        - output_file: Temporary audio filename (string)
        
        Output:
        - Transcribed text content (string)
        """
        try:
            print(f"Starting recording for {duration} seconds...")
            # Recording
            recording = sd.rec(int(duration * sample_rate), 
                             samplerate=sample_rate, 
                             channels=1, 
                             dtype='int16')
            sd.wait()  # Wait for recording completion
            
            # Save audio file
            write(output_file, sample_rate, recording)
            print("Recording completed, starting transcription...")
            
            # Transcription
            result = self.model.transcribe(output_file, language=language)
            
            # Clean up temporary files
            if os.path.exists(output_file):
                os.remove(output_file)
                
            return result["text"]
            
        except Exception as e:
            print(f"Recording transcription error: {e}")
            return ""
    
    def transcribe_batch(self, audio_file_list: list, language: str = "ko") -> dict:
        """
        Batch transcribe audio files
        
        Input:
        - audio_file_list: List of audio file paths (list of strings)
        - language: Language recognition code (string)
        
        Output:
        - Dictionary of filenames and transcription results (dict: {filename: transcribed_text})
        """
        results = {}
        try:
            for audio_file in audio_file_list:
                if os.path.exists(audio_file):
                    result = self.model.transcribe(audio_file, language=language)
                    results[audio_file] = result["text"]
                else:
                    results[audio_file] = "File not found"
                    
            return results
            
        except Exception as e:
            print(f"Batch transcription error: {e}")
            return {}


def demo():
    """
    STT module demo - Based on original STTdemo logic
    """
    # Initialize STT module
    stt = STTModule("small")
    
    # Example 1: Transcribe existing audio file
    if os.path.exists("recorded.wav"):
        result = stt.transcribe_from_file("recorded.wav", language="ko")
        print("인식 결과:", result)
    
    # Example 2: Record and transcribe
    # result = stt.record_and_transcribe(duration=5, language="ko")
    # print("Recording recognition result:", result)
    
    print("STT 모듈 초기화 완료")


if __name__ == "__main__":
    demo()