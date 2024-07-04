import React, { useState, useEffect, useContext, useRef } from 'react';
import { SocketContext } from '../App';
import './AudioRecorder.css'; // Import the CSS file for styling

const AudioRecorder = () => {
  const [recording, setRecording] = useState(false);
  const [prompt, setPrompt] = useState("");
  const currentTagRef = useRef(null);
  const socket = useContext(SocketContext);
  const audioQueueRef = useRef([]); // Queue to hold audio files
  const isPlayingRef = useRef(false); // Track if audio is currently playing

  useEffect(() => {
    if (socket) {
      socket.on('tts_audio', (data) => {
        console.log('Audio received:', data.prompt)
        setPrompt(data.prompt);
        if (data.tag) {
          currentTagRef.current = data.tag;
          console.log('Tag received:', data.tag);
        }
        if (data.categories) {
          console.log(data.categories);
        }
        audioQueueRef.current.push(data.audio); // Add the new audio to the queue
        playNextAudio(); // Attempt to play the next audio in the queue
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

  const playNextAudio = () => {
    if (!isPlayingRef.current && audioQueueRef.current.length > 0) {
      const audioData = audioQueueRef.current.shift(); // Get the next audio from the queue
      isPlayingRef.current = true; // Mark audio as playing
      playAudio(audioData).then(() => {
        isPlayingRef.current = false; // Mark audio as not playing
        if (audioQueueRef.current.length > 0) {
          playNextAudio(); // Play the next audio if there's more in the queue
        } else {
          if (!currentTagRef.current || currentTagRef.current !== 'no_response') {
            startRecording();
          }
        }
      });
    }
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
