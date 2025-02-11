import { useTransition, animated } from '@react-spring/web'
import dayjs from 'dayjs'
import { useState, useMemo, useCallback, useEffect } from 'react'
import useSWR from 'swr'
import { z } from 'zod'

import { RELATIVE_BASE_URL } from '@/lib/astro'
import { useTemporalPeriodicCallback } from '@/lib/hooks/useTemporalPeriodicCallback'
import {
  CircularTheme,
  type Definition as CircularThemeDefinition,
} from '@/lib/theme/circularTheme'
import {
  PizzaTheme,
  type Definition as PizzaThemeDefinition,
} from '@/lib/theme/pizzaTheme'

export const settingsSchema = z.object({
  theme: z.enum(['pizza_12p', 'circular']).default('pizza_12p'),
  clockTextPosition: z
    .enum(['circular_bottom_right', 'center'])
    .default('circular_bottom_right'),
  fontSize: z.number().min(10).max(100).default(30),
  letterSpacing: z.number().min(0).max(20).default(5),
  secondsIndicatorLineWidth: z.number().min(0).max(10).default(0),
})
export type Settings = z.infer<typeof settingsSchema>

type Props = { settings: Settings }

type ThemeDefinition = PizzaThemeDefinition | CircularThemeDefinition

const themeDefinitions: {
  [K in Settings['theme']]: { definitionPath: string }
} = {
  pizza_12p: { definitionPath: '/theme/pizza_12p.json' },
  circular: { definitionPath: '/theme/circular.json' },
}

const fetcher = async <JSON = unknown,>(
  input: RequestInfo,
  init?: RequestInit,
): Promise<JSON> => {
  const res = await fetch(input, init)
  return res.json()
}

export const PizzaClock = ({ settings }: Props) => {
  const [bg, setBg] = useState<{ url: string; flip: boolean }>({
    url: '',
    flip: false,
  })
  const [currentSec, setCurrentSec] = useState(0)

  const { data } = useSWR<ThemeDefinition>(
    RELATIVE_BASE_URL + themeDefinitions[settings.theme].definitionPath,
    fetcher,
  )

  const theme = useMemo(() => {
    if (!data) {
      return
    }

    if (data.type === 'pizza') {
      return new PizzaTheme(data, 'increase_decrease')
    } else {
      return new CircularTheme(data)
    }
  }, [data])

  const changeBackground = useCallback(async () => {
    if (!data || !theme) {
      return
    }

    const file = theme.chooseFile(dayjs().hour())
    if (!file) {
      return
    }

    setBg({ url: file.path, flip: file.flip })
  }, [data, theme, setBg])

  useTemporalPeriodicCallback('minutes', changeBackground, true)

  const transitions = useTransition(bg, {
    key: bg,
    from: { opacity: 0, transform: 'scale(1.8)' },
    enter: { opacity: 1, transform: 'scale(1.0)' },
    leave: { opacity: 0, transform: 'scale(0.8)' },
    config: { duration: 500 },
    exitBeforeEnter: true,
  })

  const onClickImage = () => {
    changeBackground()
  }

  useEffect(() => {
    let animationFrameId = 0

    const update = () => {
      setCurrentSec(dayjs().second() + dayjs().millisecond() / 1000)
      animationFrameId = requestAnimationFrame(update)
    }

    animationFrameId = requestAnimationFrame(update)

    return () => {
      cancelAnimationFrame(animationFrameId)
    }
  }, [])

  return (
    <>
      <div className="group flex size-full items-center justify-center bg-black">
        {transitions((style, bg) => (
          <animated.div
            className="absolute left-0 top-0 z-0 size-full bg-contain bg-center bg-no-repeat will-change-[opacity,transform]"
            style={{
              ...style,
              backgroundImage: `url(${bg.url})`,
              transform: bg.flip ? 'scaleX(-1)' : undefined,
            }}
          />
        ))}
        <div
          className="absolute z-10 flex size-full justify-center"
          onClick={onClickImage}
        >
          <svg viewBox="0 0 200 200" className="grow-0 select-none">
            {settings.secondsIndicatorLineWidth &&
              ((currentSec) => {
                const angle = (currentSec / 60) * 360
                const radians = ((angle - 90) * Math.PI) / 180
                const radius = 100 - 1
                const x = 100 + radius * Math.cos(radians)
                const y = 100 + radius * Math.sin(radians)
                const largeArcFlag = angle <= 180 ? '0' : '1'

                return (
                  <path
                    d={`M 100 1 A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x} ${y}`}
                    className="fill-transparent stroke-slate-600"
                    style={{ strokeWidth: settings.secondsIndicatorLineWidth }}
                  />
                )
              })(currentSec)}
            {settings.clockTextPosition === 'circular_bottom_right' && (
              <>
                <path
                  id="curve"
                  d="M15,100a85,85 0 1,0 170,0a85,85 0 1,0 -170,0"
                  className="fill-transparent"
                />
                <text dx={130}>
                  <textPath
                    xlinkHref="#curve"
                    className="fill-gray-100 stroke-gray-800 stroke-1 font-russoOne"
                    style={{
                      fontSize: `${settings.fontSize}px`,
                      letterSpacing: `${settings.letterSpacing}px`,
                    }}
                  >
                    {dayjs().format('HH:mm')}
                  </textPath>
                </text>
              </>
            )}
            {settings.clockTextPosition === 'center' && (
              <>
                <text
                  x="50%"
                  y="50%"
                  dx="1%"
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className="fill-gray-100 stroke-gray-800 stroke-1 font-russoOne"
                  style={{
                    fontSize: `${settings.fontSize}px`,
                    letterSpacing: `${settings.letterSpacing}px`,
                  }}
                >
                  {dayjs().format('HH:mm')}
                </text>
              </>
            )}
          </svg>
        </div>
      </div>
    </>
  )
}
