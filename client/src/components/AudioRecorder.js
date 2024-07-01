import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';

const socket = io('http://localhost:5001');

const AudioRecorder = () => {
  const [recording, setRecording] = useState(false);

  useEffect(() => {
    // Handle TTS audio from the backend
    socket.on('tts_audio', (data) => {
      playAudio(data);
    });

    // Cleanup the socket connection on component unmount
    return () => {
      socket.off('tts_audio');
    };
  }, []);

  const handleAudioInput = async () => {
    const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(audioStream, { mimeType: 'audio/webm' });
    let audioChunks = [];

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
      const reader = new FileReader();
      reader.readAsArrayBuffer(audioBlob);
      reader.onloadend = () => {
        socket.emit('audio', reader.result);
      };
    };

    mediaRecorder.start();
    setRecording(true);

    setTimeout(() => {
      mediaRecorder.stop();
      setRecording(false);
    }, 5000); // Record for 5 seconds
  };

  const playAudio = (audioData) => {
    const audioBlob = new Blob([audioData], { type: 'audio/mp3' });
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    console.log("playing audio:");
    audio.play();
  };

  return (
    <div>
      <h1>Audio Recorder</h1>
      <button onClick={handleAudioInput} disabled={recording}>
        {recording ? 'Recording...' : 'Record Audio'}
      </button>
    </div>
  );
};

export default AudioRecorder;
