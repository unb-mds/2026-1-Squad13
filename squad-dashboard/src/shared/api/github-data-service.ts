import { useState, useEffect } from 'react'
import type { GithubData } from '@/entities/github-data'

const DATA_URL = `${import.meta.env.BASE_URL}data/github-stats.json`

export function useGithubData(): { data: GithubData | null; loading: boolean; error: boolean } {
  const [data, setData] = useState<GithubData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    fetch(DATA_URL)
      .then(r => {
        if (!r.ok) throw new Error('not found')
        return r.json()
      })
      .then((d: GithubData) => {
        // placeholder file has generatedAt: null — treat as unavailable
        if (!d.generatedAt) {
          setError(true)
          return
        }
        setData(d)
      })
      .catch(() => { 
        setError(true)
      })
      .finally(() => setLoading(false))
  }, [])

  return { data, loading, error }
}
