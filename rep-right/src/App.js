import Logo from './Components/Images/RepRight.png'
import './App.css';

function App() {
  return (
      <div className="App">

          <header className="Header">
              <img className="Logo" src={Logo} alt="Logo"></img>


          </header>
          <main className="Body">
              <div className="Container">
                  <h1>Welcome to RepRight</h1>
                  <p>
                      Search for a exercise you are interested in improving for
                      real time help!!
                  </p>
                  <div className="Featured-Exercies">
                      <div className="Squat">
                          <h2>
                              Featured Exercise: Squats
                          </h2>
                          <button>Click here to work on squats!</button>
                      </div>

                  </div>
              </div>

          </main>
      </div>
  );
}

export default App;
