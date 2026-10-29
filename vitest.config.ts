/**
 * @fileoverview Vitest configuration for Light DOM custom elements and
 * gallery shell managers.
 */

import fs from 'node:fs';
import path from 'node:path';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [
    {
      name: 'resolve-ts-from-js',
      enforce: 'pre',
      resolveId(source, importer) {
        if (!importer || !source.startsWith('.') || !source.endsWith('.js')) {
          return null;
        }
        const tsCandidate = path.resolve(
          path.dirname(importer),
          source.slice(0, -3) + '.ts',
        );
        if (fs.existsSync(tsCandidate)) {
          return tsCandidate;
        }
        return null;
      },
    },
  ],
  test: {
    environment: 'happy-dom',
    environmentOptions: {
      happyDOM: {
        settings: {
          enableIframePageLoading: true,
          handleDisabledFileLoadingAsSuccess: true,
        },
      },
    },
    include: ['tests/ts/**/*.test.ts'],
    restoreMocks: true,
  },
});
