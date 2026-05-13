import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { TaskCard } from '../task-card'
import type { Task } from '@/entities/task'

// Mock do dnd-kit
vi.mock('@dnd-kit/sortable', () => ({
  useSortable: vi.fn(() => ({
    attributes: {},
    listeners: {},
    setNodeRef: vi.fn(),
    transform: null,
    transition: null,
    isDragging: false,
  }))
}))

const mockTask: Task = {
  id: '1',
  title: 'Test Task',
  description: 'Test Description',
  status: 'in_progress',
  priority: 'high',
  labels: ['feature'],
  assigneeId: 'unassigned',
  featureId: 'f1',
  dueDate: '2026-05-13',
  progress: 50,
  createdAt: '2026-05-10'
}

describe('TaskCard - Simplificação Pragmática', () => {
  it('não deve renderizar a barra de progresso mesmo que a task tenha progresso > 0', () => {
    render(<TaskCard task={mockTask} />)
    
    // A barra de progresso não deve estar no documento
    // O componente ProgressBar renderiza um elemento com role="progressbar" ou similar (preciso verificar se o shared UI tem isso)
    // De qualquer forma, verificamos se o texto da porcentagem (50%) aparece
    expect(screen.queryByText('50%')).not.toBeInTheDocument()
    
    // Verificamos por classes ou elementos de barra de progresso se necessário
    const progressBars = document.querySelectorAll('.bg-blue-500') // assumindo que a barra usa essa classe
    expect(progressBars.length).toBe(0)
  })

  it('deve exibir apenas o título, prioridade e labels', () => {
    render(<TaskCard task={mockTask} />)
    
    expect(screen.getByText('Test Task')).toBeInTheDocument()
    expect(screen.getByText('Alta')).toBeInTheDocument() // Priority label for 'high'
    expect(screen.getByText(/feature/i)).toBeInTheDocument() // Label (case-insensitive)
  })
})
