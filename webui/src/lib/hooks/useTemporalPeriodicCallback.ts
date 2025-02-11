import dayjs from 'dayjs'
import { useEffect } from 'react'

export const useTemporalPeriodicCallback = (
  onEvery: dayjs.ManipulateType,
  cb: () => Promise<void>,
  immediate: boolean = false,
) => {
  useEffect(() => {
    let latestTimerId: number
    const wait = (ms: number) =>
      new Promise((resolve) => (latestTimerId = window.setTimeout(resolve, ms)))
    const waitStartOf = (unit: dayjs.ManipulateType) =>
      wait(dayjs().startOf(unit).add(1, unit).diff())

    const runRecursively = (): Promise<void> =>
      cb()
        .then(() => waitStartOf(onEvery))
        .then(() => runRecursively())

    if (immediate) {
      runRecursively()
    } else {
      waitStartOf(onEvery).then(() => runRecursively())
    }

    return () => {
      clearTimeout(latestTimerId)
    }
  }, [onEvery, cb, immediate])
}
