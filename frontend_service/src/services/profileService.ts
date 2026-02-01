export interface Profile {
  id: string
  created_at: string
}

export async function fetchProfiles(): Promise<Profile[]> {
  try {
    const response = await fetch('/api/database/profiles')
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Failed to fetch profiles:', error)
    return []
  }
}
