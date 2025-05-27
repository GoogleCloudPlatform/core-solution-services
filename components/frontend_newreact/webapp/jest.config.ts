import type { Config } from 'jest';

const esModules = [
  /** react-markdown 9.0.1 */
  'react-markdown',
  'bail',
  'comma-separated-tokens',
  'decode-named-character-reference',
  'devlop/lib/default',
  'estree-util-is-identifier-name',
  'hast-util-.*',
  'html-url-attributes',
  'is-plain-obj',
  'mdast-util-.*',
  'micromark.*',
  'property-information',
  'remark-.*',
  'space-separated-tokens',
  'trim-lines',
  'trough',
  'unified',
  'unist-.*',
  'vfile-message',
  /** react-markdown 8.0.3 */
  'vfile',
].join('|')

// In the config:
const config: Config = {
  moduleNameMapper: {
    '^@/lib/(.*)$': '<rootDir>/src/lib/$1',
    // Add other aliases if you have them
    '\\.(css|less|scss|sass)$': '<rootDir>/__mocks__/styleMock.js',
    'next/router': '<rootDir>/_mocks_/next/router.js',
  '^.+\\.module\\.(css|sass|scss)$': 'identity-obj-proxy',
  'react-markdown': '<rootDir>/ReactMarkdownMock.tsx',
  "react-syntax-highlighter": "<rootDir>/ReactSyntaxHighlighterMock.tsx", // Mock for react-syntax-highlighter
  "^@/(.*)$": "<rootDir>/src/$1",
  "react-pdf": "<rootDir>/ReactPdfMock.tsx",
  '\\.svg$': '<rootDir>/__mocks__/svgMock.js',
  },
  preset: 'ts-jest', // Ensure TypeScript support
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
  },
  moduleFileExtensions: ['js', 'jsx', 'ts', 'tsx'],
  clearMocks: true,
  collectCoverage: true,
  coverageDirectory: 'coverage',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'], // Ensure this file exists
  testMatch: ['<rootDir>/__tests__/components/ChatScreen.test.tsx'], // Match any 'test.tsx' file anywhere
  transformIgnorePatterns: [
   `[/\\\\]node_modules[/\\\\](?!(${esModules})).+\\.(js|jsx|mjs|cjs|ts|tsx)$`,
  ],
};

export default config;