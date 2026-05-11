import { useState, useEffect } from 'react'
import type { GithubData } from '@/entities/github-data'

const DATA_URL = `${import.meta.env.BASE_URL}data/github-stats.json`

export function useGithubData(): { data: GithubData | null; loading: boolean } {
  const [data, setData] = useState<GithubData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(DATA_URL)
      .then(r => {
        if (!r.ok) throw new Error('not found')
        return r.json()
      })
      .then((d: GithubData) => {
        // placeholder file has generatedAt: null — treat as unavailable
        if (!d.generatedAt) return
        setData(d)
      })
      .catch(() => { /* silently fall back to mocks */ })
      .finally(() => setLoading(false))
  }, [])

  return { data, loading }
}
