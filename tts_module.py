"""
Text-to-Speech (TTS) Module using OpenAI API
"""

from typing import Optional, Union
import os
import openai
from pathlib import Path
from dotenv import load_dotenv
class TTSModule:
    def __init__(self, api_key: Optional[str] = None, voice_model: str = "tts-1", voice: str = "nova"):
        """
        Initialize the TTS module

        Args:
        - api_key: OpenAI API key (if not using environment variable)
        - voice_model: TTS model name ("tts-1", "tts-1-hd", etc.)
        - voice: Voice name ("alloy", "nova", "shimmer", etc.)
        """
        load_dotenv(dotenv_path=".env")
        openai.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.voice_model = voice_model
        self.voice = voice
        self.language = "ko"  # Not directly used, for future compatibility

    def text_to_speech_file(self, input_text: str, output_file: str = "output.mp3") -> str:
        """
        Convert text to a speech audio file

        Args:
        - input_text: text to convert
        - output_file: path to save .mp3 audio

        Returns:
        - output file path
        """
        try:
            response = openai.audio.speech.create(
                model=self.voice_model,
                voice=self.voice,
                input=input_text,
                response_format="mp3"
            )

            with open(output_file, "wb") as f:
                f.write(response.content)

            return output_file
        except Exception as e:
            print(f"TTS file generation error: {e}")
            return ""

    def text_to_speech_bytes(self, text: str) -> bytes:
        """
        Convert text to speech and return audio as byte data

        Args:
        - text: text to convert

        Returns:
        - audio byte content
        """
        try:
            response = openai.audio.speech.create(
                model=self.voice_model,
                voice=self.voice,
                input=text,
                response_format="mp3"
            )
            return response.content
        except Exception as e:
            print(f"TTS byte generation error: {e}")
            return b""

    def batch_text_to_speech(self, text_list: list, output_dir: str = "./audio_output") -> dict:
        """
        Batch TTS processing

        Returns:
        - dict of text => generated file path
        """
        os.makedirs(output_dir, exist_ok=True)
        result = {}
        for i, text in enumerate(text_list):
            filename = os.path.join(output_dir, f"output_{i+1}.mp3")
            path = self.text_to_speech_file(text, filename)
            result[text] = path
        return result

    def set_voice_parameters(self, voice_model: Optional[str] = None, voice: Optional[str] = None):
        """
        Update voice model or speaker
        """
        if voice_model:
            self.voice_model = voice_model
        if voice:
            self.voice = voice


def demo():
    tts = TTSModule()
    sample_text = "안녕하세요. OpenAI 음성 합성 테스트입니다."
    file_path = tts.text_to_speech_file(sample_text, "test_ko.mp3")
    print("Audio saved to:", file_path)


if __name__ == "__main__":
    demo()
