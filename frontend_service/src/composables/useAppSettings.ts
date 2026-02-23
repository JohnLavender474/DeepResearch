import { ref } from 'vue'


export type ResponseMode = 'decomposed' | 'simple'
export type ThemeMode = 'dark' | 'light'


const RESPONSE_MODE_KEY = 'deepresearch_response_mode'
const THEME_MODE_KEY = 'deepresearch_theme_mode'

const responseMode = ref<ResponseMode>('decomposed')
const themeMode = ref<ThemeMode>('light')

const availableThemeModes: ThemeMode[] = [
  'dark',
  'light',
]


const getStoredResponseMode = (): ResponseMode => {
  const storedValue = localStorage.getItem(RESPONSE_MODE_KEY)
  if (storedValue === 'simple' || storedValue === 'decomposed') {
    return storedValue
  }
  return 'decomposed'
}

const isThemeMode = (value: string | null): value is ThemeMode => {
  if (!value) {
    return false
  }

  return availableThemeModes.includes(value as ThemeMode)
}

const getStoredThemeMode = (): ThemeMode => {
  const storedValue = localStorage.getItem(THEME_MODE_KEY)
  if (isThemeMode(storedValue)) {
    return storedValue
  }

  return 'light'
}

const applyThemeMode = (mode: ThemeMode): void => {
  document.documentElement.setAttribute('data-theme', mode)
}

const initializeSettings = (): void => {
  if (typeof window === 'undefined') {
    return
  }

  responseMode.value = getStoredResponseMode()
  themeMode.value = getStoredThemeMode()
  applyThemeMode(themeMode.value)
}

const setResponseMode = (mode: ResponseMode): void => {
  responseMode.value = mode
  localStorage.setItem(RESPONSE_MODE_KEY, mode)
}

const setThemeMode = (mode: ThemeMode): void => {
  themeMode.value = mode
  applyThemeMode(mode)
  localStorage.setItem(THEME_MODE_KEY, mode)
}

export const useAppSettings = () => {
  initializeSettings()

  return {
    responseMode,
    themeMode,
    setResponseMode,
    setThemeMode,
  }
}
