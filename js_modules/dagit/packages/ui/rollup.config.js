/* eslint-disable import/no-default-export */

import babel from '@rollup/plugin-babel';
import commonjs from '@rollup/plugin-commonjs';
import image from '@rollup/plugin-image';
import json from '@rollup/plugin-json';
import resolve from '@rollup/plugin-node-resolve';
import styles from 'rollup-plugin-styles';
import url from '@rollup/plugin-url';
import polyfills from 'rollup-plugin-polyfill-node';
import nodeGlobals from 'rollup-plugin-node-globals';

const extensions = ['.js', '.jsx', '.ts', '.tsx', '.css', '.svg'];

export default {
  input: './src/index.ts',
  output: {
    dir: 'dist',
    format: 'esm',
    sourcemap: true,
  },
  plugins: [
    styles(),
    json(),
    url(),
    image(),
    babel({
      babelHelpers: 'bundled',
      exclude: 'node_modules/**',
      extensions: ['.js', '.jsx', '.ts', '.tsx'],
    }),
    commonjs(),
    polyfills(),
    nodeGlobals(),
    resolve({extensions, preferBuiltins: false}),
  ],
  external: [
    'lodash',
    'react',
    'react-dom',
    'styled-components',
  ],
};
