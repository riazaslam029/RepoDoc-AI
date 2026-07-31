import { useState, useEffect, useCallback } from 'react'
import { AnalysisStatus } from '../types'

export function useAnalysis() {
  const [status, setStatus] = useState<AnalysisStatus>({
    status: 'idle',
    progress: 0,
    message: '',
  })

  const startAnalysis = useCallback(async (repoUrl: string) => {
    setStatus({ status: 'analyzing', progress: 0, message: 'Fetching repository...' })

    try {
      const response = await fetch('/api/v1/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Analysis failed')
      }

      const data = await response.json()
      setStatus({ status: 'complete', progress: 100, message: 'Analysis complete!' })
      return data
    } catch (error) {
      setStatus({ status: 'error', progress: 0, message: error instanceof Error ? error.message : 'Unknown error' })
      throw error
    }
  }, [])

  return { status, startAnalysis }
}