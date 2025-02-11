import { glob } from 'glob'

import { pathParser, type Definition } from '../../lib/theme/pizzaTheme'

import { RELATIVE_BASE_URL } from '@/lib/astro'

const definition: Definition = {
  type: 'pizza',
  files: (await glob('public/assets/pizza_12p/*webp'))
    .map((v) => v.replace('public/', RELATIVE_BASE_URL + '/'))
    .map(pathParser),
}

export async function GET() {
  return new Response(JSON.stringify(definition, null, 4))
}
