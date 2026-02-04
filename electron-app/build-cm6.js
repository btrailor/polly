#!/usr/bin/env node

/**
 * Build script for bundling CodeMirror 6 module
 */

const esbuild = require('esbuild');
const path = require('path');

async function build() {
  try {
    await esbuild.build({
      entryPoints: [path.join(__dirname, 'src/renderer/markdown-editor-cm6.js')],
      bundle: true,
      format: 'iife',
      globalName: 'MarkdownEditorCM6',
      outfile: path.join(__dirname, 'src/renderer/markdown-editor-cm6.bundle.js'),
      minify: false,
      sourcemap: true,
      target: 'es2020',
      platform: 'browser',
      external: [],
      define: {
        'process.env.NODE_ENV': '"production"'
      }
    });
    
    console.log('[Build] CodeMirror 6 module bundled successfully');
  } catch (error) {
    console.error('[Build] Error bundling CodeMirror 6:', error);
    process.exit(1);
  }
}

build();
