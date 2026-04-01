// Learn more: https://docs.expo.dev/guides/customizing-metro/
const { getDefaultConfig } = require('expo/metro-config');

/** @type {import('expo/metro-config').MetroConfig} */
const config = getDefaultConfig(__dirname);

// expo-openclaw-chat ships TypeScript source only (no dist/).
// Ensure it is not excluded from transpilation.
config.resolver.unstable_enablePackageExports = true;

module.exports = config;
