import React, { useState, useRef, useEffect } from 'react';

const AudioRecorder = () => {
  const [recording, setRecording] = useState(false);
  const [blobURL, setBlobURL] = useState('');
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const silenceTimeoutRef = useRef(null);
  const silenceDetectedRef = useRef(false);
  const bufferPeriodRef = useRef(true);

  useEffect(() => {
    if (recording) {
      startRecording();
    } else {
      stopRecording();
    }
  }, [recording]);

  const startRecording = () => {
    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const audioURL = URL.createObjectURL(audioBlob);
        setBlobURL(audioURL);
        transcribeAudio(audioBlob);
        console.log('Recorded Blob:', audioBlob);
        audioChunksRef.current = [];
      };

      mediaRecorder.start();
      bufferPeriodRef.current = true; // Start buffer period
      setTimeout(() => {
        bufferPeriodRef.current = false; // End buffer period after 2 seconds
        detectSilence(stream, 3000);
      }, 2000);
    });
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
  };

  const detectSilence = (stream, silenceDelay) => {
    const audioContext = new AudioContext();
    const mediaStreamSource = audioContext.createMediaStreamSource(stream);
    const analyser = audioContext.createAnalyser();
    mediaStreamSource.connect(analyser);
    analyser.fftSize = 2048; // Increased fftSize for better frequency resolution
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    const silenceThreshold = 100; // Adjust the threshold for silence detection

    const checkSilence = () => {
      if (!bufferPeriodRef.current) { // Skip silence detection during buffer period
        analyser.getByteFrequencyData(dataArray);
        const sum = dataArray.reduce((a, b) => a + b, 0);
        if (sum < silenceThreshold) {
          if (!silenceDetectedRef.current) {
            silenceDetectedRef.current = true;
            console.log('Silence detected');
            silenceTimeoutRef.current = setTimeout(() => {
              if (silenceDetectedRef.current) {
                console.log('Silence detected for 3 seconds');
                silenceDetectedRef.current = false; // Reset the silence detection
              }
            }, silenceDelay);
          }
        } else {
          silenceDetectedRef.current = false;
          clearTimeout(silenceTimeoutRef.current);
        }
      }
      requestAnimationFrame(checkSilence);
    };

    checkSilence();
  };

  const transcribeAudio = async (blob) => {
    // Placeholder transcription function, replace with actual transcription service
    const transcript = 'Transcription of the recorded audio';
    console.log('Transcription:', transcript);
  };

  return (
    <div>
      <div>
        <button onClick={() => setRecording(true)} type="button">Start</button>
        <button onClick={() => setRecording(false)} type="button">Stop</button>
        {blobURL && <button onClick={() => playAudio(blobURL)} type="button">Play</button>}
      </div>
    </div>
  );
};

const playAudio = (url) => {
  const audio = new Audio(url);
  audio.play();
};

export default AudioRecorder;
