// tooling/eslint/boundaries.js — the dependency rules of docs/ARCHITECTURE.md §4 as lint (eslint-plugin-boundaries).
// Imports flow downward only. Checked in CI (`pnpm lint`) and on package manifests (`pnpm check:manifests`).
module.exports = {
  plugins: ['boundaries'],
  settings: {
    'boundaries/elements': [
      { type: 'app',       pattern: 'apps/*/*' },
      { type: 'features',  pattern: 'packages/features' },
      { type: 'api',       pattern: 'packages/api' },
      { type: 'ui',        pattern: 'packages/ui' },
      { type: 'contracts', pattern: 'packages/contracts' },
      { type: 'platform',  pattern: 'packages/platform' },
      { type: 'testing',   pattern: 'packages/testing' },
      { type: 'domainlib', pattern: ['packages/rubric-score', 'packages/cares-score'] },
    ],
  },
  rules: {
    'boundaries/element-types': ['error', {
      default: 'disallow',
      rules: [
        { from: 'app',       allow: ['features', 'api', 'ui', 'contracts', 'platform', 'domainlib', 'testing'] },
        { from: 'features',  allow: ['api', 'ui', 'contracts', 'platform', 'domainlib'] },
        { from: 'api',       allow: ['contracts', 'platform'] },
        { from: 'ui',        allow: ['platform'] },          // tokens and utilities only
        { from: 'contracts', allow: ['platform'] },          // result and utils only
        { from: 'domainlib', allow: ['contracts', 'platform'] },
        { from: 'testing',   allow: ['contracts', 'platform', 'api'] },
        { from: 'platform',  allow: [] },
      ],
    }],
    'boundaries/no-unknown': 'error',
    'no-restricted-imports': ['error', { patterns: [
      { group: ['@opentelemetry/*', '@datadog/*', '@sentry/*'], message: 'Vendor telemetry only inside packages/platform/telemetry.' },
      { group: ['**/apps/web/*/src/**'], message: 'Apps never import each other; move shared code to packages/features or packages/api.' },
    ] }],
  },
};
