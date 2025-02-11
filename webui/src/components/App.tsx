import { useEffect } from 'react'

import { settingsSchema, PizzaClock, type Settings } from './PizzaClock'
import { SettingSidebar } from './SettingSidebar'

import { useSharedState } from '@/lib/hooks/useSharedState'

const defaultSettings: Settings = {
  theme: 'pizza_12p',
  clockTextPosition: 'circular_bottom_right',
  fontSize: 30,
  letterSpacing: 5,
  secondsIndicatorLineWidth: 0,
}

const useSettings = () => {
  const [settings, setSettings] = useSharedState('settings', defaultSettings)

  return [settings, setSettings] as const
}

type Props = {
  versionString?: string
}

export const App = ({ versionString }: Props) => {
  const [settings, setSettings] = useSettings()

  // Decode settings from URL fragment on mount
  // IDEA: Watch also fragment changes
  useEffect(() => {
    try {
      const hash = window.location.hash.slice(1)
      if (hash) {
        const decoded = atob(hash)
        const parsed = settingsSchema.parse(JSON.parse(decoded))
        setSettings(parsed)
      }
    } catch (e) {
      console.error('Failed to parse settings from hash', e)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Encode and set settings into URL fragment on settings change
  useEffect(() => {
    const encoded = btoa(JSON.stringify(settings))
    window.location.hash = encoded
  }, [settings])

  return (
    <>
      <SettingSidebar
        settingsChangeHandler={setSettings}
        settings={settings}
        versionString={versionString ?? ''}
      />
      <PizzaClock settings={settings} />
    </>
  )
}
