import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Mic, MicOff, Sparkles } from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';

interface VoiceInputButtonProps {
  onTranscript: (text: string) => void;
  onListeningStart?: () => void;
  onListeningEnd?: () => void;
  className?: string;
}

export const VoiceInputButton: React.FC<VoiceInputButtonProps> = ({
  onTranscript,
  onListeningStart,
  onListeningEnd,
  className = ''
}) => {
  const { language } = useLanguage();
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);
  const isManuallyStoppedRef = useRef(false);
  const finalTranscriptRef = useRef('');

  // Map language codes to speech recognition BCP-47 tags
  const getLangCode = useCallback((lang: string): string => {
    const map: Record<string, string> = {
      en: 'en-US',
      hi: 'hi-IN',
      gu: 'gu-IN',
      mr: 'mr-IN',
      ta: 'ta-IN',
      te: 'te-IN',
      bn: 'bn-IN',
      es: 'es-ES',
      fr: 'fr-FR',
      de: 'de-DE',
      ja: 'ja-JP',
      zh: 'zh-CN',
      ar: 'ar-SA',
      pt: 'pt-BR',
      ru: 'ru-RU'
    };
    return map[lang] || 'en-US';
  }, []);

  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setIsSupported(false);
    }
  }, []);

  const stopListening = useCallback(() => {
    isManuallyStoppedRef.current = true;
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {}
      recognitionRef.current = null;
    }
    setIsListening(false);
    setStatusMessage(null);
    onListeningEnd?.();
  }, [onListeningEnd]);

  const startListening = useCallback(async () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech-to-Text is not supported by your browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    // Request browser permission explicitly if getUserMedia is available
    if (navigator.mediaDevices?.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        // Immediately release stream tracks as SpeechRecognition will manage its own audio
        stream.getTracks().forEach((track) => track.stop());
      } catch (permissionErr) {
        console.warn('Microphone permission request error:', permissionErr);
        setStatusMessage('Mic permission denied. Please allow microphone in browser.');
        alert('Microphone access was denied. Please click the lock or site settings icon in your browser address bar and set Microphone to "Allow".');
        return;
      }
    }

    try {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (e) {}
        recognitionRef.current = null;
      }

      finalTranscriptRef.current = '';
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;
      recognition.lang = getLangCode(language);
      isManuallyStoppedRef.current = false;

      recognition.onstart = () => {
        setIsListening(true);
        setStatusMessage('Listening... Speak now.');
        onListeningStart?.();
      };

      recognition.onresult = (event: any) => {
        let interimTranscript = '';
        let currentFinal = '';

        for (let i = 0; i < event.results.length; ++i) {
          const res = event.results[i];
          if (res.isFinal) {
            currentFinal += res[0].transcript + ' ';
          } else {
            interimTranscript += res[0].transcript;
          }
        }

        const fullSpoken = (currentFinal + interimTranscript).trim();
        if (fullSpoken) {
          onTranscript(fullSpoken);
        }
      };

      recognition.onerror = (event: any) => {
        console.warn('Speech recognition error event:', event.error);
        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
          setStatusMessage('Microphone access blocked. Please allow mic in browser.');
          alert('Microphone access is blocked in your browser. Please allow microphone access in site settings.');
          stopListening();
        } else if (event.error === 'no-speech') {
          // Keep listening
        } else if (event.error === 'network') {
          setStatusMessage('Network speech recognition error.');
          stopListening();
        }
      };

      recognition.onend = () => {
        if (!isManuallyStoppedRef.current && isListening) {
          try {
            recognition.start();
            return;
          } catch (e) {}
        }
        setIsListening(false);
        setStatusMessage(null);
        onListeningEnd?.();
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err: any) {
      console.warn('Could not start recognition:', err);
      setIsListening(false);
      onListeningEnd?.();
    }
  }, [language, getLangCode, onTranscript, onListeningStart, onListeningEnd, stopListening, isListening]);

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (e) {}
      }
    };
  }, []);

  if (!isSupported) {
    return null;
  }

  return (
    <div className="relative inline-flex items-center">
      <button
        type="button"
        onClick={toggleListening}
        title={isListening ? 'Click to stop recording voice' : `Click to speak voice prompt (${getLangCode(language)})`}
        className={`relative p-2.5 rounded-xl transition-all duration-300 flex items-center justify-center cursor-pointer ${
          isListening
            ? 'bg-rose-600 text-white shadow-lg shadow-rose-600/50 ring-2 ring-rose-400 scale-105 animate-pulse'
            : 'bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700'
        } ${className}`}
      >
        {isListening ? (
          <div className="flex items-center space-x-1.5">
            <MicOff className="w-4 h-4 text-white animate-bounce" />
            <span className="text-[10px] font-bold uppercase tracking-wider hidden sm:inline">Listening...</span>
          </div>
        ) : (
          <Mic className="w-4 h-4 text-cyan-400 hover:text-cyan-300" />
        )}

        {isListening && (
          <span className="absolute -top-1 -right-1 flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>
          </span>
        )}
      </button>

      {statusMessage && isListening && (
        <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 px-2.5 py-1 bg-slate-900 border border-slate-700 text-cyan-300 text-[10px] rounded-lg shadow-xl whitespace-nowrap z-30 flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-cyan-400 animate-spin" />
          <span>{statusMessage}</span>
        </div>
      )}
    </div>
  );
};
