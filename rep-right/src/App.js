import React, { useState } from "react";
import Logo from './Components/Images/RepRight.png';
import './App.css';

function Squat({ squatDis }) {
  if (squatDis) {
    return (
      <div>
        <h1>Pose Estimation</h1>
        <img
          src="http://localhost:5000/video_feed"
          alt="Video Feed"
          style={{ width: '100%', maxWidth: '800px' }}
        />
      </div>
    );
  } else {
    return null;
  }
}

function App() {
  const [squatDis, setSquatDisp] = useState(false);

  const handleClick = () => setSquatDisp(!squatDis);

  return (
    <div className="App">
      <header className="Header">
        <img className="Logo" src={Logo} alt="Logo" />
      </header>
      <main className="Body">
        <div className="Container">
          <h1>Welcome to RepRight</h1>
          <p>
            Search for an exercise you are interested in improving for real-time help!!
          </p>
          <div className="Featured-Exercises">
            <div className="Squat">
              <h2>Featured Exercise: Squats</h2>
              <button onClick={handleClick}>
                {squatDis ? 'Stop Squat Exercise' : 'Click here to work on squats!'}
              </button>
            </div>
          </div>
          <Squat squatDis={squatDis} />
        </div>
      </main>
    </div>
  );
}

export default App;
