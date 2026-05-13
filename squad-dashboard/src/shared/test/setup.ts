import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

// Mock ResizeObserver for Recharts compatibility with jsdom
class ResizeObserverMock {
  observe = vi.fn()
  unobserve = vi.fn()
  disconnect = vi.fn()
}

;(globalThis as any).ResizeObserver = ResizeObserverMock

afterEach(() => {
  cleanup()
})
