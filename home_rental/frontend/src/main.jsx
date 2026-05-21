import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  // ❌ REMOVED StrictMode — it causes double WebSocket connections in dev
  <BrowserRouter>
    <App />
    <Toaster
      position="top-right"
      toastOptions={{
        duration: 4000,
        style: {
          fontFamily: 'DM Sans, sans-serif',
          fontSize: '0.9rem',
          borderRadius: '12px',
          padding: '12px 16px',
        },
        success: {
          style: { background: '#dcfce7', color: '#15803d' },
          iconTheme: { primary: '#16a34a', secondary: '#fff' },
        },
        error: {
          style: { background: '#fee2e2', color: '#b91c1c' },
          iconTheme: { primary: '#dc2626', secondary: '#fff' },
        },
      }}
    />
  </BrowserRouter>
)