import type Profile from '@/model/profile'
import type ProfileCreate from '@/model/profileCreate'


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

export async function createProfile(
  profile: ProfileCreate
): Promise<Profile> {
  const response = await fetch('/api/database/profiles', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(profile),
  })

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null)
    const message =
      errorBody?.detail ??
      `Failed to create profile: ${response.status}`
    throw new Error(message)
  }

  const data = await response.json()

  try {
    const collectionResponse = await fetch(
      `/api/embeddings/collections/${profile.id}`,
      {
        method: 'POST',
      }
    )

    if (!collectionResponse.ok) {
      console.error(
        `Failed to create collection for profile ${profile.id}: ${collectionResponse.status}`
      )
    }
  } catch (error) {
    console.error(
      `Failed to create collection for profile ${profile.id}:`,
      error
    )
  }

  return data
}
