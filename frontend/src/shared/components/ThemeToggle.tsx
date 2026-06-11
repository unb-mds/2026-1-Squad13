import { Sun, Moon, Laptop } from 'lucide-react';
import { useTheme } from '@/shared/contexts/ThemeContext';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="flex items-center gap-1 bg-secondary/50 p-1 rounded-lg border border-border">
      <button
        onClick={() => setTheme('light')}
        className={`p-1.5 rounded-md transition-all ${
          theme === 'light' ? 'bg-card text-primary shadow-sm' : 'text-muted-foreground hover:text-foreground'
        }`}
        title="Modo Claro"
      >
        <Sun size={16} />
      </button>
      <button
        onClick={() => setTheme('dark')}
        className={`p-1.5 rounded-md transition-all ${
          theme === 'dark' ? 'bg-card text-primary shadow-sm' : 'text-muted-foreground hover:text-foreground'
        }`}
        title="Modo Escuro"
      >
        <Moon size={16} />
      </button>
      <button
        onClick={() => setTheme('system')}
        className={`p-1.5 rounded-md transition-all ${
          theme === 'system' ? 'bg-card text-primary shadow-sm' : 'text-muted-foreground hover:text-foreground'
        }`}
        title="Seguir Sistema"
      >
        <Laptop size={16} />
      </button>
    </div>
  );
}
