import React from 'react';
import starLogo from '../star_logo.png';

function Header() {
  return (
    <header className="App-header">
      <div className="header-content">
        <img src={starLogo} alt="Star Micronics Logo" className="App-logo" />
        <h1 className="header-title">Dynamic Pricing Dashboard</h1>
      </div>
    </header>
  );
}

export default Header;
