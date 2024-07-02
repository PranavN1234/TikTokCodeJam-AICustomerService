import React, { useState, useEffect, useContext, useRef } from 'react';
import { SocketContext } from '../App';
import './AudioRecorder.css'; // Import the CSS file for styling

const AudioRecorder = () => {
  const [recording, setRecording] = useState(false);
  const [prompt, setPrompt] = useState("");
  const currentTagRef = useRef(null);
  const socket = useContext(SocketContext);

  useEffect(() => {
    if (socket) {
      socket.on('tts_audio', (data) => {
        setPrompt(data.prompt);
        if (data.tag) {
          currentTagRef.current = data.tag;
          console.log('Tag received:', data.tag);
        }
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
        console.log('tag emitted', currentTagRef.current);
        socket.emit('audio_response', { audio: reader.result, tag: currentTagRef.current });
        currentTagRef.current = null; 
      };
    };

    mediaRecorder.start();
    setRecording(true);

    setTimeout(() => {
      mediaRecorder.stop();
      setRecording(false);
    }, 5000); 
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
    <div className="audio-recorder">
      <div className={`button-container ${recording ? 'recording' : ''}`}>
        <button className="record-button" onClick={startRecording}>
          {recording ? 'Recording...' : 'Start Recording'}
        </button>
      </div>
      <p>{prompt}</p>
    </div>
  );
};

export default AudioRecorder;
