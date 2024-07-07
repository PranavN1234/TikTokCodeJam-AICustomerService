import React, { useEffect, useState, createContext } from 'react';
import { io } from 'socket.io-client';
import AudioRecorder from './components/AudioRecorder';
import './App.css'; // Import the CSS file for styling
import { IconButton } from '@mui/material';
import CallIcon from '@mui/icons-material/Call';
import CallEndIcon from '@mui/icons-material/CallEnd';
import { styled } from '@mui/material/styles';

export const SocketContext = createContext();

const GreenCallButton = styled(IconButton)({
  backgroundColor: 'green',
  color: 'white',
  '&:hover': {
    backgroundColor: 'darkgreen',
  },
  borderRadius: '50%',
  padding: '10px',
});

const RedCallEndButton = styled(IconButton)({
  backgroundColor: 'red',
  color: 'white',
  '&:hover': {
    backgroundColor: 'darkred',
  },
  borderRadius: '50%',
  padding: '10px',
});

function App() {
  const [socketInstance, setSocketInstance] = useState(null);
  const [buttonStatus, setButtonStatus] = useState(false);

  const handleClick = () => {
    setButtonStatus(!buttonStatus);
  };

  useEffect(() => {
    if (buttonStatus) {
      const socket = io('http://localhost:5001', {
        transports: ['websocket'],
        cors: {
          origin: 'http://localhost:3000',
          methods: ['GET', 'POST'],
          allowedHeaders: ['my-custom-header'],
          credentials: true,
        },
      });

      setSocketInstance(socket);

      socket.on('connect', () => {
        console.log('Connected to backend');
        socket.emit('start');
      });

      socket.on('disconnect', () => {
        console.log('Disconnected from backend');
      });

      return () => {
        socket.disconnect();
      };
    }
  }, [buttonStatus]);

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Customer Service Assistant</h1>
        {buttonStatus ? (
          <RedCallEndButton onClick={handleClick}>
            <CallEndIcon />
          </RedCallEndButton>
        ) : (
          <GreenCallButton onClick={handleClick}>
            <CallIcon />
          </GreenCallButton>
        )}
      </header>
      <div className="content">
        <div className="main-content">
          <SocketContext.Provider value={socketInstance}>
            <AudioRecorder buttonStatus={buttonStatus} setButtonStatus={setButtonStatus} />
          </SocketContext.Provider>
        </div>
      </div>
    </div>
  );
}

export default App;
