import React, { useState, useEffect, useContext } from 'react';
import { SocketContext } from '../App';

const AudioRecorder = () => {
  const [recording, setRecording] = useState(false);
  const [prompt, setPrompt] = useState("");
  const socket = useContext(SocketContext);

  useEffect(() => {
    if (socket) {
      socket.on('tts_audio', (data) => {
        setPrompt(data.prompt);
        playAudio(data.audio).then(() => {
          startRecording();
        });
      });

      return () => {
        socket.off('tts_audio');
      };
    }
  }, [socket]);

  const startRecording = async () => {
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
        socket.emit('audio_response', reader.result);
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
    return new Promise((resolve) => {
      const audioBlob = new Blob([audioData], { type: 'audio/mp3' });
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
      audio.onended = resolve;
    });
  };

  return (
    <div>
      <h1>Audio Recorder</h1>
      <p>{prompt}</p>
      {recording && <p>Recording...</p>}
    </div>
  );
};

export default AudioRecorder;
