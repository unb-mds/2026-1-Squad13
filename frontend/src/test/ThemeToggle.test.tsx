import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, useTheme } from '../shared/contexts/ThemeContext';
import { ThemeToggle } from '../shared/components/ThemeToggle';

describe('ThemeToggle', () => {
  it('renderiza os botoes de tema e permite mudar de tema', () => {
    // Mock matchMedia do window
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation(query => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });

    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    // Verifica os botoes por title
    const lightBtn = screen.getByTitle('Modo Claro');
    const darkBtn = screen.getByTitle('Modo Escuro');
    const systemBtn = screen.getByTitle('Seguir Sistema');

    expect(lightBtn).toBeInTheDocument();
    expect(darkBtn).toBeInTheDocument();
    expect(systemBtn).toBeInTheDocument();

    // Clica no botao do modo escuro
    fireEvent.click(darkBtn);

    // Clica no botao de seguir sistema
    fireEvent.click(systemBtn);
  });

  it('lanca erro se usar useTheme fora de ThemeProvider', () => {
    const ComponenteSemProvider = () => {
      useTheme();
      return null;
    };

    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => render(<ComponenteSemProvider />)).toThrow(
      'useTheme must be used within a ThemeProvider'
    );

    consoleSpy.mockRestore();
  });
});

