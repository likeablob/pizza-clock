import { exec } from 'node:child_process'
import { promisify } from 'node:util'

const execAsync = promisify(exec)

export const getGitInfo = async () => {
  let versionInfo: { shortHash: string | undefined; tag: string | undefined } =
    {
      shortHash: undefined,
      tag: undefined,
    }
  try {
    const shortHash = await execAsync('git rev-parse HEAD')
      .then(({ stdout: v }) => v.trim().slice(0, 8))
      .catch(() => undefined)
    const tag = await execAsync('git describe --tags --exact-match')
      .then(({ stdout: v }) => v.trim())
      .catch(() => undefined)
    versionInfo = {
      shortHash,
      tag,
    }
  } catch (e) {
    console.error('Failed to get git info', e)
  }
  return versionInfo
}
