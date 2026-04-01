/**
 * gatewayCapabilities.ts — Fetch and store gateway version + capabilities on connect.
 *
 * Spec: phase-1-ios-foundation/tasks.md — "Post-connection: config.get →
 * store gateway version + capabilities in MMKV"
 *
 * Called once per successful connection (after auth.ok). Stores results in
 * MMKV so UI components can read them synchronously without async calls.
 *
 * MMKV keys (non-sensitive — credentials stay in SecureStore):
 *   polly.gateway.version       string
 *   polly.gateway.capabilities  JSON string (string[])
 *   polly.gateway.fetchedAt     ISO 8601 timestamp
 */

import { MMKV } from 'react-native-mmkv';
import { sanitizeForLog } from '../utils/sanitizeForLog';
import type { GatewayClient, GatewayMessage } from './GatewayClient';

const storage = new MMKV({ id: 'polly-gateway-meta' });

export const GATEWAY_META_KEYS = {
  VERSION: 'polly.gateway.version',
  CAPABILITIES: 'polly.gateway.capabilities',
  FETCHED_AT: 'polly.gateway.fetchedAt',
} as const;

export interface GatewayCapabilities {
  version: string;
  capabilities: string[];
  fetchedAt: string;
}

/**
 * Read stored gateway capabilities from MMKV.
 * Returns null if not yet fetched (e.g. first launch before first connect).
 */
export function getStoredGatewayCapabilities(): GatewayCapabilities | null {
  const version = storage.getString(GATEWAY_META_KEYS.VERSION);
  const capabilitiesRaw = storage.getString(GATEWAY_META_KEYS.CAPABILITIES);
  const fetchedAt = storage.getString(GATEWAY_META_KEYS.FETCHED_AT);

  if (!version || !capabilitiesRaw || !fetchedAt) return null;

  try {
    const capabilities = JSON.parse(capabilitiesRaw) as string[];
    return { version, capabilities, fetchedAt };
  } catch {
    return null;
  }
}

/**
 * Fetch gateway version + capabilities via config.get, store in MMKV.
 *
 * Sends a config.get request and waits for the response via onMessage.
 * Times out after 5 seconds — non-fatal, app continues without capabilities.
 *
 * @param client - the active GatewayClient (must be connected)
 */
export async function fetchAndStoreGatewayCapabilities(
  client: GatewayClient
): Promise<GatewayCapabilities | null> {
  return new Promise((resolve) => {
    const timeoutHandle = setTimeout(() => {
      console.warn('[gatewayCapabilities] config.get timed out — proceeding without capabilities');
      unsubscribe();
      resolve(null);
    }, 5_000);

    const unsubscribe = client.onMessage((message: GatewayMessage) => {
      if (message.type !== 'config.get.response') return;

      clearTimeout(timeoutHandle);
      unsubscribe();

      try {
        const version = (message.gatewayVersion as string) ?? 'unknown';
        const capabilities = Array.isArray(message.capabilities)
          ? (message.capabilities as string[])
          : [];
        const fetchedAt = new Date().toISOString();

        storage.set(GATEWAY_META_KEYS.VERSION, version);
        storage.set(GATEWAY_META_KEYS.CAPABILITIES, JSON.stringify(capabilities));
        storage.set(GATEWAY_META_KEYS.FETCHED_AT, fetchedAt);

        console.log(
          '[gatewayCapabilities] Stored:',
          sanitizeForLog({ version, capabilityCount: capabilities.length })
        );

        resolve({ version, capabilities, fetchedAt });
      } catch (err) {
        console.error('[gatewayCapabilities] Failed to store capabilities:', sanitizeForLog(err));
        resolve(null);
      }
    });

    // Send the config.get request
    try {
      (client as unknown as { ws: WebSocket | null }).ws?.send(
        JSON.stringify({ type: 'config.get' })
      );
    } catch (err) {
      console.error('[gatewayCapabilities] Failed to send config.get:', sanitizeForLog(err));
      clearTimeout(timeoutHandle);
      unsubscribe();
      resolve(null);
    }
  });
}
