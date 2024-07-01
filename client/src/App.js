import React, { useEffect, useState } from 'react';
import { io } from 'socket.io-client';
import AudioRecorder from './components/AudioRecorder';

function App() {
  const [socketInstance, setSocketInstance] = useState(null);
  const [loading, setLoading] = useState(true);
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
      });

      socket.on('disconnect', () => {
        console.log('Disconnected from backend');
      });

      setLoading(false);

      return () => {
        socket.disconnect();
      };
    }
  }, [buttonStatus]);

  return (
    <div className="App">
      <h1>React/Flask App + socket.io</h1>
      {!buttonStatus ? (
        <button onClick={handleClick}>Turn Chat On</button>
      ) : (
        <>
          <button onClick={handleClick}>Turn Chat Off</button>
          <div className="line">
            {!loading && socketInstance && <AudioRecorder socket={socketInstance} />}
          </div>
        </>
      )}
    </div>
  );
}

export default App;
