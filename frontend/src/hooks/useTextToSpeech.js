import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * useTextToSpeech
 *
 * Manages browser-native window.speechSynthesis for reading text aloud.
 * Detects support, exposes speaking state, and cleans up on unmount.
 *
 * Default config is tuned to sound natural rather than robotic:
 *   - lang:   en-US
 *   - rate:   0.95  (slightly slower than default 1.0 for clarity)
 *   - pitch:  1.0   (normal pitch)
 *   - volume: 1.0   (full volume)
 */

const DEFAULT_CONFIG = {
  lang: 'en-US',
  rate: 0.95,
  pitch: 1.0,
  volume: 1.0,
};

const useTextToSpeech = (config = {}) => {
  const mergedConfig = { ...DEFAULT_CONFIG, ...config };

  const [isSupported, setIsSupported] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [error, setError] = useState(null);

  // Track the active utterance so we can cancel it
  const utteranceRef = useRef(null);

  // Detect support once on mount
  useEffect(() => {
    setIsSupported(
      typeof window !== 'undefined' &&
        'speechSynthesis' in window &&
        typeof window.SpeechSynthesisUtterance !== 'undefined'
    );

    // Cleanup: cancel any ongoing speech when the component unmounts
    return () => {
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  /**
   * speak(text) — synthesise the given text string.
   * Cancels any previous utterance first so replaying is safe.
   */
  const speak = useCallback(
    (text) => {
      if (!isSupported) {
        setError('Text-to-speech is not supported in this browser.');
        return;
      }

      if (!text || !text.trim()) return;

      // Cancel whatever might already be playing
      window.speechSynthesis.cancel();
      setError(null);

      const utterance = new window.SpeechSynthesisUtterance(text.trim());
      utterance.lang = mergedConfig.lang;
      utterance.rate = mergedConfig.rate;
      utterance.pitch = mergedConfig.pitch;
      utterance.volume = mergedConfig.volume;

      utterance.onstart = () => {
        setIsSpeaking(true);
        setError(null);
      };

      utterance.onend = () => {
        setIsSpeaking(false);
      };

      utterance.onerror = (event) => {
        // 'interrupted' / 'canceled' are expected when stop() is called —
        // don't show an error to the user for those cases.
        if (event.error === 'interrupted' || event.error === 'canceled') {
          setIsSpeaking(false);
          return;
        }
        setIsSpeaking(false);
        setError('Could not read the question aloud. Please read it on screen.');
        console.error('SpeechSynthesis error:', event.error);
      };

      utteranceRef.current = utterance;
      window.speechSynthesis.speak(utterance);
    },
    [isSupported, mergedConfig.lang, mergedConfig.rate, mergedConfig.pitch, mergedConfig.volume]
  );

  /**
   * stop() — immediately cancel any in-progress speech.
   */
  const stop = useCallback(() => {
    if (!isSupported) return;
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  }, [isSupported]);

  /**
   * clearError() — dismiss the current TTS error message.
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    isSupported,
    isSpeaking,
    error,
    speak,
    stop,
    clearError,
  };
};

export default useTextToSpeech;
