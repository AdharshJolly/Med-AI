"""
Voice Handler for MedAI-Pro Chatbot
Speech-to-text and text-to-speech functionality
"""

import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pathlib import Path
from typing import Optional, Dict
from loguru import logger
import os
import tempfile


class VoiceHandler:
    """Handle voice input and output for chatbot"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.supported_languages = {
            'en': 'en-US',
            'hi': 'hi-IN',
            'bn': 'bn-IN',
            'te': 'te-IN',
            'ta': 'ta-IN',
            'mr': 'mr-IN',
            'gu': 'gu-IN',
            'kn': 'kn-IN',
            'ml': 'ml-IN',
            'pa': 'pa-IN'
        }
        
        logger.info("✅ Voice Handler initialized")
    
    def speech_to_text(
        self,
        audio_file: str,
        language: str = 'en'
    ) -> Dict:
        """Convert speech to text"""
        
        result = {
            'success': False,
            'text': '',
            'language': language,
            'confidence': 0.0,
            'error': None
        }
        
        try:
            # Load audio file
            audio_path = Path(audio_file)
            
            # Convert to WAV if needed
            if audio_path.suffix.lower() not in ['.wav']:
                audio = AudioSegment.from_file(str(audio_path))
                wav_path = audio_path.with_suffix('.wav')
                audio.export(str(wav_path), format='wav')
                audio_file = str(wav_path)
            
            # Recognize speech
            with sr.AudioFile(audio_file) as source:
                audio_data = self.recognizer.record(source)
                
                # Get language code
                lang_code = self.supported_languages.get(language, 'en-US')
                
                # Perform recognition
                text = self.recognizer.recognize_google(
                    audio_data,
                    language=lang_code
                )
                
                result['success'] = True
                result['text'] = text
                result['confidence'] = 0.9  # Google API doesn't provide confidence
                
                logger.info(f"Speech recognized: {text}")
        
        except sr.UnknownValueError:
            result['error'] = "Could not understand audio"
            logger.warning("Speech not understood")
        
        except sr.RequestError as e:
            result['error'] = f"API error: {str(e)}"
            logger.error(f"Speech recognition API error: {e}")
        
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Speech-to-text error: {e}")
        
        return result
    
    def text_to_speech(
        self,
        text: str,
        language: str = 'en',
        output_file: Optional[str] = None
    ) -> Dict:
        """Convert text to speech"""
        
        result = {
            'success': False,
            'audio_file': None,
            'error': None
        }
        
        try:
            # Create output file if not provided
            if output_file is None:
                temp_dir = tempfile.gettempdir()
                output_file = os.path.join(temp_dir, f"tts_{os.urandom(8).hex()}.mp3")
            
            # Generate speech
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(output_file)
            
            result['success'] = True
            result['audio_file'] = output_file
            
            logger.info(f"Text-to-speech generated: {output_file}")
        
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Text-to-speech error: {e}")
        
        return result
    
    def record_audio(
        self,
        duration: int = 5,
        output_file: Optional[str] = None
    ) -> Dict:
        """Record audio from microphone"""
        
        result = {
            'success': False,
            'audio_file': None,
            'error': None
        }
        
        try:
            with sr.Microphone() as source:
                logger.info("Recording...")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Record audio
                audio_data = self.recognizer.listen(source, timeout=duration)
                
                # Save to file
                if output_file is None:
                    temp_dir = tempfile.gettempdir()
                    output_file = os.path.join(temp_dir, f"rec_{os.urandom(8).hex()}.wav")
                
                with open(output_file, 'wb') as f:
                    f.write(audio_data.get_wav_data())
                
                result['success'] = True
                result['audio_file'] = output_file
                
                logger.info(f"Audio recorded: {output_file}")
        
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Audio recording error: {e}")
        
        return result
    
    def process_voice_message(
        self,
        audio_file: str,
        language: str = 'en'
    ) -> Dict:
        """Complete voice message processing"""
        
        # Convert speech to text
        stt_result = self.speech_to_text(audio_file, language)
        
        if not stt_result['success']:
            return {
                'success': False,
                'error': stt_result['error'],
                'text': None
            }
        
        return {
            'success': True,
            'text': stt_result['text'],
            'language': language,
            'confidence': stt_result['confidence']
        }


if __name__ == "__main__":
    handler = VoiceHandler()
    
    # Test text-to-speech
    test_text = "Hello, I am MedAI, your medical assistant. How can I help you today?"
    tts_result = handler.text_to_speech(test_text, 'en')
    
    if tts_result['success']:
        print(f"✅ TTS generated: {tts_result['audio_file']}")
    else:
        print(f"❌ TTS failed: {tts_result['error']}")
    
    logger.info("✅ Voice Handler test completed")

