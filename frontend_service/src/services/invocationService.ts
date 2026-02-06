import type Invocation from '@/model/invocation'


const API_BASE_URL = '/api/database'


export async function fetchInvocation(
  profileId: string,
  invocationId: string
): Promise<Invocation> {
  if (!profileId) {
    throw new Error('No profile selected');
  }

  const response = await fetch(
    `${API_BASE_URL}/${profileId}/invocations/${invocationId}`
  )

  if (!response.ok) {
    throw new Error(`Failed to fetch invocation: ${response.statusText}`)
  }

  return response.json()
}
