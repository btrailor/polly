/**
 * gatewayCapabilities.ts — DEPRECATED (Phase 1A refactor)
 *
 * Capabilities fetch + storage is now handled inside PollyGatewayAdapter.
 * Re-exported here for any early imports — remove at Phase 1B cleanup.
 */

export { getStoredGatewayCapabilities, GATEWAY_META_KEYS } from './PollyGatewayAdapter';
