import random from 'just-random'

export type File = {
  category: string
  path: string
}

export type Definition = {
  type: 'pizza'
  files: File[]
}

export const pathParser = (path: string): File => {
  const { category } = /pizza_12p_(?<category>\d*p)_/.exec(path)?.groups || {}
  return {
    path,
    category,
  }
}

const CATEGORIES = [
  '0p',
  '1p',
  '2p',
  '3p',
  '4p',
  '5p',
  '6p',
  '7p',
  '8p',
  '9p',
  '10p',
  '11p',
  '12p',
] as const

type Category = (typeof CATEGORIES)[number]

/**
 * "increase_decrease": increase the number of pieces in AM (0 to 11), and decrease in PM (12 to 1)
 * "decrease_increase": vise versa
 */
type HourMappingMode = 'increase_decrease' | 'decrease_increase'

export class PizzaTheme {
  readonly definition: Definition
  readonly mode: HourMappingMode

  constructor(definition: Definition, mode: HourMappingMode) {
    this.definition = definition
    this.mode = mode
  }

  setMode(mode: HourMappingMode) {
    return new PizzaTheme(this.definition, mode)
  }

  hourToCategory(hour: number): { category: Category; flip: boolean } {
    const ind = hour % 12 // 0 - 11
    const incCategory = CATEGORIES[ind] // 0p - 11p
    const decCategory = CATEGORIES.toReversed()[ind] // 12p - 1p
    const incRes = { category: incCategory, flip: false }
    const decRes = { category: decCategory, flip: true }
    const isAM = hour < 12

    if (this.mode === 'increase_decrease') {
      return isAM ? incRes : decRes
    }

    return isAM ? decRes : incRes
  }

  chooseFile(hour: number): (File & { flip: boolean }) | undefined {
    const { category, flip } = this.hourToCategory(hour)
    const file = random(
      this.definition.files.filter((v) => v.category === category),
    )

    return file && { ...file, flip }
  }
}
