import React, { useState, useEffect, useContext, useRef } from 'react';
import { SocketContext } from '../App';
import Avatar from '@mui/material/Avatar';
import './AudioRecorder.css'; // Import the CSS file for styling
import jessicaImage from './jessica.webp'; // Ensure the path to your image is correct
import blockCardImage from '../assets/Block_Card.webp'; // Path to your images
import changeInfoImage from '../assets/Change_Information.webp';
import issueNewCardImage from '../assets/Issue_New_card.webp';
import flagFraudImage from '../assets/fraudulant_transaction.webp';
import bankInfoImage from '../assets/bank_information.webp';
import chitchatImage from '../assets/chitchat.webp';
import { Typewriter } from 'react-simple-typewriter';
import { BallTriangle } from 'react-loader-spinner';
import beepaudio from './beep.mp3';
import PieChartComponent from './PieChartComponent';

const AudioRecorder = () => {
  const [recording, setRecording] = useState(false);
  const [prompt, setPrompt] = useState("");
  const currentTagRef = useRef(null);
  const socket = useContext(SocketContext);
  const audioQueueRef = useRef([]); // Queue to hold audio files
  const promptQueueRef = useRef([]);
  const isPlayingRef = useRef(false); // Track if audio is currently playing
  const [loadingText, setLoadingText] = useState("");
  const [showLoader, setShowLoader] = useState(false);
  const [currentImage, setCurrentImage] = useState(null);
  const [creditLimit, setCreditLimit] = useState(null);
  const [interestRate, setInterestRate] = useState(null);
  const silenceTimeoutRef = useRef(null);
  const [categories, setCategories] = useState(null); 

  useEffect(() => {
    if (socket) {
      socket.on('tts_audio', (data) => {
        if (data.tag) {
          currentTagRef.current = data.tag;
          console.log('Tag received:', data.tag);
        }
        if (data.clear_input) {
          setShowLoader(false);
          setLoadingText("");
          setCurrentImage(null);
          setCreditLimit(null);
          setInterestRate(null);
        }
        if (data.credit_limit && data.interest_rate) {
          setShowLoader(false);
          setCreditLimit(data.credit_limit);
          setInterestRate(data.interest_rate);
        }
        if (data.categories) {
          console.log(data.categories);
          setCategories(data.categories); // Set the categories data
        }
        promptQueueRef.current.push(data.prompt);
        audioQueueRef.current.push(data.audio); // Add the new audio to the queue
        playNextAudio(); // Attempt to play the next audio in the queue
      });

      socket.on('add-input', (data) => {
        setShowLoader(true);
        setLoadingText(data.loadingText);
        if(data.image){
          setCurrentImage(data.image);
        }
      });

      return () => {
        socket.off('tts_audio');
        socket.off('add-input');
      };
    }
  }, [socket]);

  const startRecording = async () => {
    const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(audioStream, { mimeType: 'audio/webm' });
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const input = audioContext.createMediaStreamSource(audioStream);
    const analyser = audioContext.createAnalyser();
    input.connect(analyser);
    analyser.fftSize = 2048;
    const bufferLength = analyser.fftSize;
    const dataArray = new Uint8Array(bufferLength);
    let audioChunks = [];
    let silenceStart = null;
    const silenceThreshold = 2; // Silence threshold in seconds

    const checkForSilence = () => {
      analyser.getByteTimeDomainData(dataArray);
      let isSilent = true;
      for (let i = 0; i < bufferLength; i++) {
        if (dataArray[i] > 128 + 5 || dataArray[i] < 128 - 5) {
          isSilent = false;
          break;
        }
      }
      if (isSilent) {
        if (silenceStart === null) {
          silenceStart = Date.now();
        } else {
          const silenceDuration = (Date.now() - silenceStart) / 1000;
          if (silenceDuration >= silenceThreshold) {
            mediaRecorder.stop();
            clearInterval(silenceTimeoutRef.current);
          }
        }
      } else {
        silenceStart = null;
      }
    };

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

    silenceTimeoutRef.current = setInterval(checkForSilence, 200); // Check for silence every 200ms
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

  const getImage = (imageName) => {
    switch(imageName) {
      case 'block-card.webp':
        return blockCardImage;
      case 'change-information.webp':
        return changeInfoImage;
      case 'issue-new-card.webp':
        return issueNewCardImage;
      case 'flag-fraud.webp':
        return flagFraudImage;
      case 'bank-info.webp':
        return bankInfoImage;
      case 'chitchat.webp':
        return chitchatImage;
      default:
        return null;
    }
  };

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
              typeSpeed={100} // Adjusted typeSpeed for faster typing
              deleteSpeed={50}
              delaySpeed={1000} // Adjusted delaySpeed for faster response
            />
          </div>
        </div>
        <div className="additional-info-container">
          {showLoader ? (
            <div className="additional-info-box">
              {currentImage && <img src={getImage(currentImage)} alt="Current Task" style={{ width: '100%', height: 'auto' }} />}
              <BallTriangle color="#00BFFF" height={80} width={80} />
              <p>{loadingText}</p>
            </div>
          ) : creditLimit && interestRate ? (
            <div className="additional-info-box">
              <p>Credit Limit: {creditLimit}</p>
              <p>Interest Rate: {interestRate}%</p>
            </div>
          ) : categories ? (
            <div className="additional-info-box pie-chart-container">
              <PieChartComponent data={categories} />
            </div>     
          ) : (
            <div className="additional-info-box">
              <p>Additional information</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AudioRecorder;
