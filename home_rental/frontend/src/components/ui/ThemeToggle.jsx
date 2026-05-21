import { Sun, Moon } from 'lucide-react'
import useThemeStore from '../../store/useThemeStore'

export default function ThemeToggle() {
  const { theme, toggleTheme } = useThemeStore()

  return (
    <button
      onClick={toggleTheme}
      title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
      style={{
        width:        38,
        height:       38,
        borderRadius: '50%',
        border:       '1.5px solid var(--border)',
        background:   'var(--bg-card)',
        display:      'flex',
        alignItems:   'center',
        justifyContent: 'center',
        cursor:       'pointer',
        color:        'var(--text-primary)',
        transition:   'all 0.2s',
        flexShrink:   0,
      }}
      onMouseEnter={e => {
        e.currentTarget.style.borderColor = 'var(--ochre)'
        e.currentTarget.style.color       = 'var(--ochre)'
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = 'var(--border)'
        e.currentTarget.style.color       = 'var(--text-primary)'
      }}
    >
      {theme === 'light'
        ? <Moon size={16} />
        : <Sun  size={16} />
      }
    </button>
  )
}