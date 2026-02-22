import { ref } from 'vue'


export type ResponseMode = 'decomposed' | 'simple'


const RESPONSE_MODE_KEY = 'deepresearch_response_mode'

const responseMode = ref<ResponseMode>('decomposed')


const getStoredResponseMode = (): ResponseMode => {
  const storedValue = localStorage.getItem(RESPONSE_MODE_KEY)
  if (storedValue === 'simple' || storedValue === 'decomposed') {
    return storedValue
  }
  return 'decomposed'
}

const initializeSettings = (): void => {
  if (typeof window === 'undefined') {
    return
  }
  responseMode.value = getStoredResponseMode()
}

const setResponseMode = (mode: ResponseMode): void => {
  responseMode.value = mode
  localStorage.setItem(RESPONSE_MODE_KEY, mode)
}

export const useAppSettings = () => {
  initializeSettings()

  return {
    responseMode,
    setResponseMode,
  }
}
