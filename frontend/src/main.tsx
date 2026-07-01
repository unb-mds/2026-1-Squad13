import React from 'react'
import ReactDOM from 'react-dom/client'
import { AppRouter } from './app/router'
import { ThemeProvider } from './shared/contexts/ThemeContext'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <AppRouter />
    </ThemeProvider>
  </React.StrictMode>
)
