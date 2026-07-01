import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useDebounce } from '../shared/lib/hooks/use-debounce';

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('retorna o valor inicial imediatamente', () => {
    const { result } = renderHook(() => useDebounce('teste', 500));
    expect(result.current).toBe('teste');
  });

  it('nao atualiza o valor antes do delay estipulado', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'inicial', delay: 500 } }
    );

    // Atualiza prop
    rerender({ value: 'alterado', delay: 500 });
    expect(result.current).toBe('inicial');

    // Avanca o tempo parcialmente
    act(() => {
      vi.advanceTimersByTime(200);
    });
    expect(result.current).toBe('inicial');

    // Avanca o restante do tempo
    act(() => {
      vi.advanceTimersByTime(300);
    });
    expect(result.current).toBe('alterado');
  });

  it('limpa o timeout anterior quando valor muda rapidamente', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'inicial', delay: 500 } }
    );

    rerender({ value: 'meio', delay: 500 });
    
    act(() => {
      vi.advanceTimersByTime(300);
    });
    expect(result.current).toBe('inicial'); // Ainda nao deu o tempo

    rerender({ value: 'final', delay: 500 });

    act(() => {
      vi.advanceTimersByTime(300); // Passaram 300ms adicionais, mas o novo timer precisava de 500ms
    });
    expect(result.current).toBe('inicial');

    act(() => {
      vi.advanceTimersByTime(200); // Totaliza 500ms do ultimo timer
    });
    expect(result.current).toBe('final');
  });
});
