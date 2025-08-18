import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from '../App'

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    // Проверяем, что приложение рендерится без ошибок
    expect(document.body).toBeInTheDocument()
  })
})
