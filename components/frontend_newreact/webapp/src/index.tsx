import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './i18n' // Import the i18n configuration
import './index.css'

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)