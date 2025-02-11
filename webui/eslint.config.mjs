import { fixupPluginRules } from '@eslint/compat'
import eslint from '@eslint/js'
import eslintConfigPrettier from 'eslint-config-prettier'
import { configs as pluginAstroConfigs } from 'eslint-plugin-astro'
import importPlugin from 'eslint-plugin-import'
import pluginJsxA11y from 'eslint-plugin-jsx-a11y'
import pluginReact from 'eslint-plugin-react'
import pluginReactHooks from 'eslint-plugin-react-hooks'
import tailwind from 'eslint-plugin-tailwindcss'
import globals from 'globals'
import {
  configs as tsEslintConfigs,
  config as tsEslintConfig,
} from 'typescript-eslint'

/**
 * @type {import('typescript-eslint').ConfigWithExtends[]'}
 */
export const defaultConfig = [
  eslint.configs.recommended,
  tsEslintConfigs.recommended,
  ...pluginAstroConfigs.recommended,
  eslintConfigPrettier,
  importPlugin.flatConfigs.recommended,
  importPlugin.flatConfigs.typescript,
  {
    ignores: ['node_modules', 'dist', '.astro'],
  },
  {
    settings: {
      'import/resolver': {
        typescript: {
          alwaysTryTypes: true,
        },
      },
    },
    rules: {
      // See https://github.com/benmosher/eslint-plugin-import/blob/master/docs/rules/order.md
      'import/order': [
        'error',
        {
          'newlines-between': 'always',
          alphabetize: {
            order: 'asc',
          },
        },
      ],
    },
  },
  {
    files: ['eslint.config.mjs', 'astro.config.mjs'],
    languageOptions: {
      globals: {
        ...globals.node,
      },
    },
  },
  {
    rules: {
      '@typescript-eslint/no-namespace': 'off',
      '@typescript-eslint/no-unused-vars': [
        'warn',
        {
          args: 'all',
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_',
        },
      ],
    },
  },
]

export default tsEslintConfig(
  ...defaultConfig,
  ...tailwind.configs['flat/recommended'],
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    plugins: {
      react: pluginReact,
      'jsx-a11y': pluginJsxA11y,
      'react-hooks': fixupPluginRules(pluginReactHooks),
    },
    rules: {
      ...pluginReact.configs.recommended.rules,
      ...pluginReact.configs['jsx-runtime'].rules,
      ...pluginJsxA11y.configs.recommended.rules,
      ...pluginReactHooks.configs.recommended.rules,
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
  },
  {
    rules: {
      'tailwindcss/classnames-order': 'off',
    },
  },
  {
    rules: {
      'jsx-a11y/click-events-have-key-events': 'off',
      'jsx-a11y/no-static-element-interactions': 'off',
    },
  },
)
