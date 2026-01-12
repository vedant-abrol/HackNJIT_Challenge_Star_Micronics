import React from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import Header from './components/Header';

function App() {
  return (
    <div className="App">
      <Header />
      <main className="main-content">
        <Dashboard />
      </main>
      <footer className="footer">
        <p>© 2024 Star Micronics - POS Receipt Data Analysis Platform</p>
      </footer>
    </div>
  );
}

export default App;
