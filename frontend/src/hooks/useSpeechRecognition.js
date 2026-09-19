import { useState, useEffect, useCallback, useRef } from 'react';

const useSpeechRecognition = (onFinalTranscript) => {
  const [isSupported, setIsSupported] = useState(true);
  const [isRecording, setIsRecording] = useState(false);
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState(null);

  const recognitionRef = useRef(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      setIsSupported(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsRecording(true);
      setError(null);
    };

    recognition.onresult = (event) => {
      let currentInterim = '';
      let currentFinal = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          currentFinal += event.results[i][0].transcript;
        } else {
          currentInterim += event.results[i][0].transcript;
        }
      }

      setInterimTranscript(currentInterim);
      
      if (currentFinal) {
        // Pass the finalized text back to the component
        onFinalTranscript(currentFinal);
      }
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error', event.error);
      setIsRecording(false);
      
      switch (event.error) {
        case 'not-allowed':
          setError('Microphone permission denied.');
          break;
        case 'no-speech':
          setError('No speech detected.');
          break;
        case 'audio-capture':
          setError('No microphone found.');
          break;
        case 'network':
          setError('Network error occurred.');
          break;
        case 'aborted':
          // User stopped it intentionally or it reset
          break;
        default:
          setError(`Error: ${event.error}`);
      }
    };

    recognition.onend = () => {
      // It can end if silence is detected for too long depending on browser, 
      // but continuous = true usually prevents this on Chrome. 
      // If it ends, we just update state.
      setIsRecording(false);
      setInterimTranscript('');
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [onFinalTranscript]);

  const startRecording = useCallback(() => {
    if (!isSupported || !recognitionRef.current) return;
    
    setError(null);
    setInterimTranscript('');
    try {
      recognitionRef.current.start();
    } catch (e) {
      console.error('Could not start recognition', e);
      setError('Failed to start recording.');
    }
  }, [isSupported]);

  const stopRecording = useCallback(() => {
    if (!isSupported || !recognitionRef.current) return;
    
    try {
      recognitionRef.current.stop();
    } catch (e) {
      console.error('Could not stop recognition', e);
    }
  }, [isSupported]);

  return {
    isSupported,
    isRecording,
    interimTranscript,
    error,
    startRecording,
    stopRecording
  };
};

export default useSpeechRecognition;
