/**
 * GatewayClient.ts — DEPRECATED (Phase 1A refactor)
 *
 * The app-level GatewayClient singleton has been retired.
 * The SDK's GatewayClient (expo-openclaw-chat/src/core/client.ts) is the
 * one true WebSocket connection, managed by PollyGatewayAdapter.
 *
 * Connection state is available via:
 *   import { useConnectionStore } from '../store/connectionStore'
 *
 * All gateway operations (send, history, abort) go through:
 *   import { PollyGatewayAdapter } from './PollyGatewayAdapter'
 *
 * TOFU, protectionLevel config.patch, and capabilities fetch are all
 * handled inside PollyGatewayAdapter.create().
 *
 * This file is kept to avoid breaking any early imports — remove at Phase 1B cleanup.
 */

export { clearTofuFingerprint, getStoredGatewayCapabilities, GATEWAY_META_KEYS } from './PollyGatewayAdapter';
