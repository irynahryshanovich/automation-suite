import React from "react";
import Dashboard from "./components/Dashboard";
import "./App.css";

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <div className="container">
          <h1>Automation Suite</h1>
        </div>
      </header>

      <main>
        <div className="container">
          <Dashboard />
        </div>
      </main>

      <footer>
        <div className="container">
          <p>
            &copy; 2026 Automation Suite. Designed and developed by Iryna
            Hryshanovich
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
