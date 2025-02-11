import useSWR, { type Key } from 'swr'

export const useSharedState = <Data>(key: Key, fallbackData?: Data) => {
  const { data: state, mutate: setState } = useSWR(key, {
    fallbackData,
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
  })

  return [state, setState]
}
