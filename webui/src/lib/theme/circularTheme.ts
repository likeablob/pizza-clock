import random from 'just-random'

export type File = {
  category: string
  path: string
}

export type Definition = {
  type: 'circular'
  files: File[]
}

export const pathParser = (path: string): File => {
  const { category } = /circular_(?<category>\d*p)_/.exec(path)?.groups || {}
  return {
    path,
    category,
  }
}

export class CircularTheme {
  readonly definition: Definition

  constructor(data: Definition) {
    this.definition = data
  }

  chooseFile() {
    const file = random(this.definition.files)

    return file && { ...file, flip: false }
  }
}
