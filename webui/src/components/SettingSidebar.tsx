import { SiGithub } from '@icons-pack/react-simple-icons'
import { SettingsIcon, Clipboard, Check } from 'lucide-react'
import { useEffect, useState } from 'react'

import type { Settings } from './PizzaClock'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { RELATIVE_BASE_URL } from '@/lib/astro'
import { cn } from '@/lib/utils'

export type SettingsChangeHandler = (newSettings: Settings) => void
type Props = {
  settingsChangeHandler: SettingsChangeHandler
  settings: Settings
  versionString: string
}

export const SettingSidebar = ({
  settingsChangeHandler,
  settings,
  versionString,
}: Props) => {
  const [open, setOpen] = useState(false)
  const [newSettings, setNewSettings] = useState(settings)
  const [isCopied, setIsCopied] = useState(false)
  const [showSettingsIcon, setShowSettingsIcon] = useState(true)

  useEffect(() => {
    settingsChangeHandler(newSettings)
  }, [newSettings, settingsChangeHandler])

  useEffect(() => {
    setTimeout(() => {
      setShowSettingsIcon(false)
    }, 3000)
  }, [])

  const copyUrl = () => {
    navigator.clipboard.writeText(window.location.href)
    setIsCopied(true)
    setTimeout(() => {
      setIsCopied(false)
    }, 1000)
  }

  const handleMouseMove = () => {
    setShowSettingsIcon(true)
    setTimeout(() => {
      setShowSettingsIcon(false)
    }, 3000)
  }

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild onClick={() => setOpen(true)}>
        <div
          className="absolute right-0 top-0 z-50"
          onMouseMove={handleMouseMove}
        >
          <button
            className={cn(
              'rounded-3xl rounded-tr-none bg-black/60 p-2 text-white transition-opacity duration-500 hover:bg-black/90',
              {
                'opacity-100': showSettingsIcon,
                'opacity-0': !showSettingsIcon,
              },
            )}
          >
            <SettingsIcon className="size-16" />
          </button>
        </div>
      </SheetTrigger>
      <SheetContent className="w-72 sm:text-right">
        <SheetHeader className="h-full">
          <SheetTitle>Settings</SheetTitle>
          <SheetDescription></SheetDescription>
          <div className="flex h-full flex-col gap-3">
            <div className="sm:col-span-3">
              <label
                htmlFor="clock-theme"
                className="block text-sm font-medium leading-6 text-gray-900"
              >
                Clock theme
              </label>
              <div id="clock-theme" className="mt-2">
                <Select
                  defaultValue={settings.theme}
                  onValueChange={(value) =>
                    setNewSettings((prev) => ({
                      ...prev,
                      theme: value as Settings['theme'],
                    }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a theme" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pizza_12p">Pizza 12p</SelectItem>
                    <SelectItem value="circular">Something Circular</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="sm:col-span-3">
              <label
                htmlFor="clock-text-position"
                className="block text-sm font-medium leading-6 text-gray-900"
              >
                Clock text position
              </label>
              <div id="clock-text-position" className="mt-2">
                <Select
                  defaultValue={settings.clockTextPosition}
                  onValueChange={(value) =>
                    setNewSettings((prev) => ({
                      ...prev,
                      clockTextPosition: value as Settings['clockTextPosition'],
                    }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a position" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="circular_bottom_right">
                      Circular bottom right
                    </SelectItem>
                    <SelectItem value="center">Center</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="sm:col-span-3">
              <label
                htmlFor="font-size"
                className="block text-sm font-medium leading-6 text-gray-900"
              >
                Font Size
              </label>
              <div id="font-size" className="mt-2">
                <Slider
                  defaultValue={[settings.fontSize]}
                  max={100}
                  min={10}
                  step={1}
                  onValueChange={(value) =>
                    setNewSettings((prev) => ({
                      ...prev,
                      fontSize: value[0],
                    }))
                  }
                />
              </div>
            </div>
            <div className="sm:col-span-3">
              <label
                htmlFor="letter-spacing"
                className="block text-sm font-medium leading-6 text-gray-900"
              >
                Letter Spacing
              </label>
              <div id="letter-spacing" className="mt-2">
                <Slider
                  defaultValue={[settings.letterSpacing]}
                  max={20}
                  min={0}
                  step={1}
                  onValueChange={(value) =>
                    setNewSettings((prev) => ({
                      ...prev,
                      letterSpacing: value[0],
                    }))
                  }
                />
              </div>
            </div>
            <div className="sm:col-span-3">
              <label
                htmlFor="minute-circle-thickness"
                className="block text-sm font-medium leading-6 text-gray-900"
              >
                Seconds Indicator Width
              </label>
              <div id="minute-circle-thickness" className="mt-2">
                <Slider
                  defaultValue={[settings.secondsIndicatorLineWidth]}
                  max={10}
                  min={0}
                  step={0.5}
                  onValueChange={(value) =>
                    setNewSettings((prev) => ({
                      ...prev,
                      secondsIndicatorLineWidth: value[0],
                    }))
                  }
                />
              </div>
            </div>
            <div className="sm:col-span-3">
              <label
                htmlFor="share-url"
                className="block text-sm font-medium leading-6 text-gray-900"
              >
                Share URL
              </label>
              <div id="share-url" className="mt-2 flex gap-1">
                <Input
                  readOnly
                  value={window.location.href}
                  className="flex-1"
                />
                <Button variant="ghost" onClick={copyUrl}>
                  {isCopied ? (
                    <Check className="size-4 text-green-500" />
                  ) : (
                    <Clipboard className="size-4" />
                  )}
                </Button>
              </div>
            </div>
            <div className="grow" />
            <div className="flex flex-col items-center justify-center gap-3">
              <a
                className="h-16 w-32 bg-contain bg-center bg-no-repeat"
                style={{
                  backgroundImage: `url(${RELATIVE_BASE_URL}/images/logo_l.png)`,
                }}
                href="https://github.com/likeablob/pizza-clock"
                target="_blank"
                rel="noreferrer"
              >
                {null}
              </a>
              <div className="text-center text-xs text-gray-500">
                {versionString}
              </div>
              <div className="flex gap-2">
                <SiGithub className="size-4" />
                <a
                  target="_blank"
                  href="https://github.com/likeablob/pizza-clock"
                  className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700"
                  rel="noreferrer"
                >
                  GitHub
                </a>
              </div>
            </div>
          </div>
        </SheetHeader>
      </SheetContent>
    </Sheet>
  )
}
