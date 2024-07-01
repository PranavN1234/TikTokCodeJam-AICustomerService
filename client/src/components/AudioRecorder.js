import React, { useState, useEffect, useRef } from 'react';

const MIN_DECIBELS = -45;
const SILENCE_DELAY = 4000; // 4 seconds

const AudioRecorder = () => {
  const [recording, setRecording] = useState(false);
  const [blobURL, setBlobURL] = useState('');
  const [silenceDetected, setSilenceDetected] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const silenceTimeoutRef = useRef(null);

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

      mediaRecorder.start();

      mediaRecorder.addEventListener("dataavailable", event => {
        audioChunksRef.current.push(event.data);
      });

      const audioContext = new AudioContext();
      const audioStreamSource = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.minDecibels = MIN_DECIBELS;
      audioStreamSource.connect(analyser);

      const bufferLength = analyser.frequencyBinCount;
      const domainData = new Uint8Array(bufferLength);

      const detectSound = () => {
        analyser.getByteFrequencyData(domainData);
        const sum = domainData.reduce((a, b) => a + b, 0);

        if (sum > 0) {
          clearTimeout(silenceTimeoutRef.current);
          setSilenceDetected(false);
          silenceTimeoutRef.current = setTimeout(() => {
            setSilenceDetected(true);
            console.log('Silence detected for 4 seconds');
          }, SILENCE_DELAY);
        }

        if (recording) {
          window.requestAnimationFrame(detectSound);
        }
      };

      window.requestAnimationFrame(detectSound);

      mediaRecorder.addEventListener("stop", () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        setBlobURL(audioUrl);
        console.log('Recorded Blob:', audioBlob);

        // Reset audio chunks
        audioChunksRef.current = [];
      });
    });
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
    clearTimeout(silenceTimeoutRef.current);
  };

  const playAudio = () => {
    const audio = new Audio(blobURL);
    audio.play();
  };

  return (
    <div>
      <div>
        <button onClick={() => setRecording(true)} type="button">Start</button>
        <button onClick={() => setRecording(false)} type="button">Stop</button>
        {blobURL && <button onClick={playAudio} type="button">Play</button>}
      </div>
      {silenceDetected && <p>Silence detected for 4 seconds</p>}
    </div>
  );
};

export default AudioRecorder;
