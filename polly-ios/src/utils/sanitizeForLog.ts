/**
 * sanitizeForLog — strips credentials from any value before console.log or crash dump.
 *
 * Scrubs:
 *   - polly.* secure store key paths (appear in error traces)
 *   - JSON fields: token, privateKey, password, tlsFingerprint
 *
 * Always returns a deep copy — never mutates the original.
 */

const STRING_PATTERNS: RegExp[] = [
  /polly\.(device|gateway|push|vault)\.[a-zA-Z]+/g,
  /"token":\s*"[^"]+"/g,
  /"privateKey":\s*"[^"]+"/g,
  /"password":\s*"[^"]+"/g,
  /"tlsFingerprint":\s*"[^"]+"/g,
];

/**
 * Scrub all sensitive patterns from a string value.
 */
function redactString(value: string): string {
  let result = value;
  for (const pattern of STRING_PATTERNS) {
    // Reset lastIndex so repeated calls don't skip matches on global regexes
    pattern.lastIndex = 0;
    result = result.replace(pattern, (match) => {
      // For JSON key-value matches (e.g. `"token": "abc"`), keep the key, redact value
      const colonIdx = match.indexOf(':');
      if (colonIdx !== -1) {
        return match.slice(0, colonIdx + 1) + ' "[REDACTED]"';
      }
      return '[REDACTED]';
    });
  }
  return result;
}

/**
 * Sensitive field names — any object key matching these will have its value replaced.
 */
const SENSITIVE_KEYS = new Set([
  'token',
  'privateKey',
  'password',
  'tlsFingerprint',
  'tunnelUrl',
  'sendKey',
  'apnsToken',
  'vaultBookmark',
  'authorization',
  'Authorization',
  'x-polly-token',
]);

export function sanitizeForLog(input: unknown): unknown {
  if (input === null || input === undefined) return input;

  if (typeof input === 'string') {
    return redactString(input);
  }

  if (typeof input === 'number' || typeof input === 'boolean') {
    return input;
  }

  if (Array.isArray(input)) {
    return input.map(sanitizeForLog);
  }

  if (typeof input === 'object') {
    const result: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(input as Record<string, unknown>)) {
      if (SENSITIVE_KEYS.has(key)) {
        result[key] = '[REDACTED]';
      } else {
        result[key] = sanitizeForLog(value);
      }
    }
    return result;
  }

  // symbol, function, bigint — return as-is
  return input;
}
