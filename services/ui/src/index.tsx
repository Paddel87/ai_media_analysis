/**
 * UC-001 Enhanced Manual Analysis - React Entry Point
 * Version: 1.0.0 - Web Interface Bootstrap
 * Status: ALPHA 0.6.0 - Power-User-First Strategy
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Create root and render app
const root = ReactDOM.createRoot(
    document.getElementById('root') as HTMLElement
);

root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);
