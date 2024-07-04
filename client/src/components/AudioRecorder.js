import React, { useState, useEffect, useContext, useRef } from 'react';
import { SocketContext } from '../App';
import Avatar from '@mui/material/Avatar';
import './AudioRecorder.css'; // Import the CSS file for styling
import jessicaImage from './jessica.webp'; // Ensure the path to your image is correct
import { Typewriter } from 'react-simple-typewriter';
import beepaudio from './beep.mp3';

const AudioRecorder = () => {
  const [recording, setRecording] = useState(false);
  const [prompt, setPrompt] = useState("");
  const currentTagRef = useRef(null);
  const socket = useContext(SocketContext);
  const audioQueueRef = useRef([]); // Queue to hold audio files
  const promptQueueRef = useRef([]);
  const isPlayingRef = useRef(false); // Track if audio is currently playing

  useEffect(() => {
    if (socket) {
      socket.on('tts_audio', (data) => {
        if (data.tag) {
          currentTagRef.current = data.tag;
          console.log('Tag received:', data.tag);
        }
        if (data.categories) {
          console.log(data.categories);
        }
        promptQueueRef.current.push(data.prompt);
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
      const audioData = audioQueueRef.current.shift(); 
      const promptText = promptQueueRef.current.shift(); 
      setPrompt(promptText);
      isPlayingRef.current = true; // Mark audio as playing
      document.querySelector('.avatar-container').classList.add('speaking'); // Add speaking class
      playAudio(audioData).then(() => {
        isPlayingRef.current = false; // Mark audio as not playing
        document.querySelector('.avatar-container').classList.remove('speaking'); // Remove speaking class
        if (audioQueueRef.current.length > 0) {
          playNextAudio(); // Play the next audio if there's more in the queue
        } else {
          if (!currentTagRef.current || currentTagRef.current !== 'no_response') {
            playBeep().then(() => startRecording());
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

  const playBeep = () => {
    return new Promise((resolve) => {
      const beepAudio = new Audio(beepaudio); // Ensure this path is correct
      beepAudio.play();
      beepAudio.onended = resolve;
    });
  };

  useEffect(() => {
    const avatarContainer = document.querySelector('.avatar-container');
    if (avatarContainer) {
      if (recording) {
        avatarContainer.classList.add('recording');
      } else {
        avatarContainer.classList.remove('recording');
      }
    }
  }, [recording]);

  return (
    <div>
      <div className="audio-recorder">
        <div className={`avatar-container ${recording ? 'recording' : ''}`}>
          <Avatar
            alt="Jessica"
            src={jessicaImage}
            className="avatar"
            sx={{ width: 300, height: 300 }}
          />
        </div>
      </div>
      <div className="info-container">
        <div className="prompt-container">
          <div className="prompt-box">
            <Typewriter
              words={[prompt]}
              loop={false}
              cursor
              cursorStyle='|'
              typeSpeed={70} // Adjusted typeSpeed for faster typing
              deleteSpeed={50}
              delaySpeed={1000} // Adjusted delaySpeed for faster response
            />
          </div>
        </div>
        <div className="additional-info-container">
          <div className="additional-info-box">
            <p>Additional information</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AudioRecorder;
