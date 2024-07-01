import React from 'react';
import './App.css';
import AudioRecorder from './components/AudioRecorder';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>React Voice Recorder</h1>
      </header>
      <main>
        <AudioRecorder />
      </main>
    </div>
  );
}

export default App;
