"""
Voice Pipeline - Speech processing pipeline
Integrates STT, LLM-RAG, and TTS modules in a main caller file.

Pipeline: Audio input → STT (speech-to-text) → LLM-RAG (text understanding and answering) 
→ TTS (convert response to speech) → Audio output

This filcontains Voice Pipeline class and several functions, which includes:
1. question answering part
    1.1 process_audio_files
    1.2 process_live_conversation
2. utilities：
    2.1 batch_process_audio_files
    2.2 add_knowledge_documents
        this function can be optimized while it has the potential to read the notion knowledge database.
"""

from stt_module import STTModule
from llm_rag_module import LLMRAGModule
from tts_module import TTSModule
import os
from typing import Optional


class VoicePipeline:
    def __init__(self, 
                 stt_model_size: str = "small",
                 llm_model_name: str = "gpt-3.5-turbo",
                 tts_voice_model: str = "default",
                 language: str = "ko"):
        """
        Initialize the voice processing pipeline
        
        Args:
        - stt_model_size: STT model size (string)
            -transcribe_from_file
            -record_and_transcribe
            -transcribe_batch
            
        - llm_model_name: LLM model name (string)
            -build_graph
            -add_documents
            -retrieve_relevant_docs
            -chat
            
        - tts_voice_model: TTS voice model (string)
        - language: processing language (string)
        """
        print("Initializing voice pipeline...")
        
        # Initialize the three modules
        self.stt = STTModule(model_size=stt_model_size)
        self.llm_rag = LLMRAGModule(model_name=llm_model_name)
        self.tts = TTSModule(voice_model=tts_voice_model, language=language)
        
        self.language = language
        print("Voice pipeline initialized successfully!")
    
    def process_audio_file(self, audio_file_path: str, output_audio_path: str = "response.wav") -> dict:
        """
        Process a single audio file - full voice interaction pipeline
        
        Args:
        - audio_file_path: input audio file path (string)
        - output_audio_path: output audio file path (string)
        
        Returns:
        - result dictionary (dict): {
            "input_text": recognized input text,
            "response_text": LLM-generated response,
            "output_audio": output audio file path,
            "success": status flag
        }
        """
        result = {
            "input_text": "",
            "response_text": "",
            "output_audio": "",
            "success": False
        }
        
        try:
            print(f"Processing audio file: {audio_file_path}")
            
            # Step 1: STT - speech to text
            print("1. Interpreting voice...")
            input_text = self.stt.transcribe_from_file(audio_file_path, language=self.language)
            if not input_text:
                print("Speech recognition failed")
                return result
            
            result["input_text"] = input_text
            print(f"Recognized: {input_text}")
            
            # Step 2: LLM-RAG - text understanding and response generation
            print("2. Generating response...")
            response_text = self.llm_rag.chat(input_text)
            if not response_text:
                print("Response generation failed")
                return result
                
            result["response_text"] = response_text
            print(f"Response: {response_text}")
            
            # Step 3: TTS - text to speech
            print("3. Synthesizing speech...")
            output_audio = self.tts.text_to_speech_file(response_text, output_audio_path)
            if not output_audio:
                print("Speech synthesis failed")
                return result
                
            result["output_audio"] = output_audio
            result["success"] = True
            print(f"Processing complete! Output audio: {output_audio}")
            
            return result
            
        except Exception as e:
            print(f"Voice pipeline processing error: {e}")
            return result
    
    def process_live_conversation(self, record_duration: int = 5, 
                                output_audio_path: str = "live_response.wav") -> dict:
        """
        Real-time conversation processing - record, recognize, respond, playback
        
        Args:
        - record_duration: recording duration in seconds (int)
        - output_audio_path: output audio path (string)
        
        Returns:
        - result dictionary (dict)
        """
        result = {
            "input_text": "",
            "response_text": "",
            "output_audio": "",
            "success": False
        }
        
        try:
            print("Starting live conversation...")
            
            # Step 1: Record and transcribe
            print("1. Please speak now...")
            input_text = self.stt.record_and_transcribe(
                duration=record_duration, 
                language=self.language
            )
            if not input_text:
                print("Recording recognition failed")
                return result
            
            result["input_text"] = input_text
            print(f"You said: {input_text}")
            
            # Step 2: Generate response
            print("2. Thinking...")
            response_text = self.llm_rag.chat(input_text)
            if not response_text:
                print("Response generation failed")
                return result
                
            result["response_text"] = response_text
            print(f"Response: {response_text}")
            
            # Step 3: Synthesize and play
            print("3. Playing response...")
            # Generate audio file
            output_audio = self.tts.text_to_speech_file(response_text, output_audio_path)
            result["output_audio"] = output_audio
            
            # Attempt stream playback
            self.tts.text_to_speech_stream(response_text)
            
            result["success"] = True
            print("Live conversation complete!")
            
            return result
            
        except Exception as e:
            print(f"Live conversation error: {e}")
            return result
    
    def batch_process_audio_files(self, audio_files: list, output_dir: str = "./batch_output") -> list:
        """
        Batch process audio files
        
        Args:
        - audio_files: list of audio file paths (List[string])
        - output_dir: output directory (string)
        
        Returns:
        - list of processing results (List[dict])
        """
        results = []
        
        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for i, audio_file in enumerate(audio_files):
            print(f"\nProcessing file {i+1}/{len(audio_files)}: {audio_file}")
            
            output_audio = os.path.join(output_dir, f"response_{i+1}.wav")
            result = self.process_audio_file(audio_file, output_audio)
            result["input_file"] = audio_file
            results.append(result)
        
        return results
    
    def add_knowledge_documents(self, documents: list) -> bool:
        """
        Add knowledge documents
        
        Args:
        - documents: list of document contents (List[string])
        
        Returns:
        - success status (bool)
        """
        return self.llm_rag.add_documents(documents)


def demo():
    """
    Voice pipeline demo
    """
    print("=== Voice Pipeline Demo ===")
    
    # Initialize voice pipeline
    pipeline = VoicePipeline(
        stt_model_size="small",
        language="ko"
    )
    
    print("\nAvailable features:")
    print("1. Process audio file: pipeline.process_audio_file('input.wav')")
    print("2. Live conversation: pipeline.process_live_conversation()")
    print("3. Batch processing: pipeline.batch_process_audio_files(['file1.wav', 'file2.wav'])")
    
    # Example: process audio file (if exists)
    if os.path.exists("recorded.wav"):
        print("\nDetected recorded.wav, starting processing...")
        result = pipeline.process_audio_file("recorded.wav")
        print(f"Result: {result}")
    
    # Example: live conversation (requires microphone)
    # print("\nStarting live conversation demo...")
    # result = pipeline.process_live_conversation(record_duration=5)
    # print(f"Live result: {result}")
    
    print("\nVoice pipeline demo complete!")


def main():
    """
    Main program entry
    """
    demo()


if __name__ == "__main__":
    main()
