# Distributed Reasoning Mesh (OpenSpec)

Source of truth for Polly's peer-to-peer distributed reasoning protocol. Enables multiple Polly instances to discover each other, share computational resources, and collaboratively process complex queries across local networks, remote tunnels, and resilient mesh radios.

## Overview

The DRM allows Polly instances to cooperate without a central coordinator. Each node runs a worker (executes tasks) and a coordinator (discovers peers, distributes work). Any node can process locally or distribute subtasks across available peers.

Three discovery/communication layers provide progressive reach and resilience:

| Layer | Scope | Latency | Bandwidth | When |
|---|---|---|---|---|
| **mDNS** | LAN / VPN | 1–10ms | Gigabit | Always (home network) |
| **Cloudflare Tunnels** | Internet | 50–150ms | Full | Remote hardware, mobile nodes |
| **Meshtastic (LoRa)** | Radio range (km) | 2–30s | 1–10 kbps | IP network unavailable, off-grid |

All three layers are optional and composable. A node can use any combination.

---

## Design Principles

- **Peer-to-peer:** No central coordinator; any node failure degrades gracefully.
- **Resource-aware:** Nodes advertise capabilities; work routes to appropriate resources.
- **Domain-specialized:** Support for specialized models per reasoning domain.
- **Network-agnostic discovery:** Pluggable discovery layer — mDNS, Cloudflare Workers, Meshtastic, or custom registry. Choose what serves your actual usage.
- **Layered connectivity:** Local-first for performance, remote for reach, radio for resilience. Each layer is independent; the system degrades gracefully as layers become unavailable.
- **Autonomous operation:** Each node fully functional independently; cluster improves performance.

## Node Identity & Capabilities

Each Polly node maintains a capability manifest:

```json
{
  "node_id": "uuid-v4",
  "hostname": "nas-polly",
  "version": "polly-drm/0.1",
  "capacity": {
    "cpu_cores": 8,
    "memory_gb": 16,
    "gpu": { "available": false, "type": null, "vram_gb": 0 },
    "disk_gb": 500
  },
  "current_load": {
    "cpu_percent": 0.25,
    "memory_percent": 0.40,
    "active_tasks": 2
  },
  "models": [
    { "domain": "sigils", "model_id": "llama3.2:3b-sigils-ft", "loaded": true, "context_window": 8192 }
  ],
  "network": {
    "local_ip": "192.168.1.100",
    "mesh_ip": "100.64.0.1",
    "tunnel_url": "https://nas-polly.yourdomain.com",
    "tunnel_id": "cf-tunnel-uuid",
    "network_type": "local",
    "rtt_ms": {}
  },
  "geography": {
    "country": "US",
    "region": "us-east",
    "label": "home-office"
  },
  "last_seen": "2026-02-08T14:32:00Z"
}
```

**New fields (vs v0.1):**
- `tunnel_url` / `tunnel_id` — Cloudflare Tunnel endpoint (null if local-only).
- `network_type` — `local` (LAN/VPN), `remote` (Cloudflare Tunnel), `mesh` (Meshtastic gateway).
- `geography` — Optional geographic tagging for data sovereignty and compliance routing.

---

## Service Discovery

### Layer 1: mDNS (Local Network)

- **Protocol:** mDNS (Multicast DNS) / DNS-SD (DNS Service Discovery).
- **Service type:** `_polly-drm._tcp.local.`
- **Discovery flow:** Node starts → broadcasts presence via mDNS → listens for peers → maintains peer registry → periodic heartbeat (30s) → prune peers not seen in 90s.
- **Zero-configuration:** Same tech as AirDrop. No central server or DNS dependency.
- **Scope:** LAN + Tailscale/Wireguard VPN mesh.

### Layer 2: Cloudflare Tunnels (Remote / Internet)

Each node runs `cloudflared` creating an outbound-only connection to Cloudflare's edge. Nodes register with a Cloudflare Workers coordination service, then communicate peer-to-peer through their respective tunnel URLs.

**Key insight:** Cloudflare handles discovery and signaling only. Once nodes know each other's tunnel endpoints, they communicate directly through Cloudflare's network as if on same LAN. You're not routing all traffic through a central service — just the peer registry.

#### Coordination Worker

A Cloudflare Worker + KV namespace acts as the remote peer registry:

```
POST /peers/register    # Register node (with auth), returns active peer list
GET  /peers/list        # List active peers
```

- Peers stored in Workers KV with 120s TTL (auto-expire stale entries).
- Worker validates mesh membership token before accepting registration.
- Deployed via Wrangler. Cost: free tier covers ~13k requests/day (5-node mesh).

#### Node Registration Flow

1. Node starts `cloudflared` tunnel (outbound-only, firewall-friendly).
2. Registers with Worker: `POST https://polly-mesh.yourdomain.workers.dev/peers/register` with JWT auth.
3. Receives list of other active nodes with their tunnel URLs.
4. Sends heartbeat every 60s to maintain registration.
5. Communicates directly with other nodes via their tunnel URLs (`POST https://peer.domain.com/tasks/submit`).

#### Tunnel Configuration

```yaml
# ~/.cloudflared/config.yml
tunnel: <tunnel-id>
credentials-file: /path/to/credentials.json

ingress:
  - hostname: nas-polly.yourdomain.com
    service: http://localhost:8765  # Polly DRM API
  - service: http_status:404
```

#### Hybrid Discovery

Both layers merge, preferring local peers for lower latency:

```python
def discover_peers(self):
    local_peers = self.mdns_discover()    # LAN neighbors
    remote_peers = self.cf_discover()      # Tunneled nodes

    for p in local_peers:
        p.network_type = "local"
        p.latency_estimate = 5   # ms

    for p in remote_peers:
        p.network_type = "remote"
        p.latency_estimate = 100  # ms

    return self.merge_peers(local_peers, remote_peers)
```

Routing logic adapts by task sensitivity:
- **Interactive queries** → local peers only (sub-100ms latency).
- **Batch processing** → anywhere (latency doesn't matter).
- **Specialized models** → wherever they exist (accept latency cost).

#### Cost Analysis

Cloudflare free tier includes: unlimited tunnels, 100k Worker requests/day, 100k KV reads/day, 1k KV writes/day, zero egress fees.

Typical 5-node mesh: ~7,200 heartbeats/day + ~6k peer/task requests = ~13k requests/day (well within free tier). Workers Paid ($5/mo) gives 10M requests for serious usage.

Compare to cloud compute: one GPU instance = $500+/mo. Your own hardware + Cloudflare = effectively free after hardware investment.

#### Exit Strategy

Cloudflare is convenience, not dependency. The coordination logic is simple enough to self-host:
- Deploy coordination Worker as standalone service on your own VPS.
- Run WireGuard mesh (Tailscale/Headscale) for direct peer connectivity.
- System continues working with different discovery mechanism.

Federation model: analogous to email. You run your own server (Polly node), use common protocol (HTTP/JSON), interoperate through neutral infrastructure. No platform lock-in.

### Layer 3: Meshtastic (LoRa Radio — Resilience)

When IP networks are unavailable, LoRa radio provides coordination-only communication. This is post-internet computing infrastructure.

#### Core Constraint

LoRa realities fundamentally reshape what "distributed" means:
- Max payload: 237 bytes per packet.
- Bandwidth: 1–10 kbps typical.
- Range: 5–30 km (line of sight).
- Latency: 2–30 seconds per hop.

LLM prompts (~1–10 KB) and responses (~1–100 KB) **cannot traverse mesh**. Meshtastic carries only coordination signals and hash references. Compute happens locally; mesh coordinates.

#### Gateway Node Architecture

Hardware: Raspberry Pi Zero 2 W + LoRa HAT (or any Meshtastic-compatible radio).
Role: Bridge between LoRa mesh and IP network.

```
[Offline laptop + Meshtastic radio]
    ↓ LoRa (task request: ~200 bytes)
[Gateway node: RPi + Meshtastic + WiFi]
    ↓ IP network
[Polly mesh: NAS, Desktop, etc.]
    ↓ Process task
[Gateway node]
    ↓ LoRa (result notification: ~200 bytes)
[Offline laptop]
    ↓ (later, when online)
[Retrieves full result via WiFi/internet]
```

#### Meshtastic Message Protocol

Uses Meshtastic `PRIVATE_APP` portnum for custom DRM messages. Payloads use msgpack for efficiency (40% smaller than JSON). Dictionary encoding for common fields.

**Task request (via mesh):**
```python
{
    "v": 1,           # protocol version
    "t": "req",       # type: request
    "id": "ab12",     # truncated task ID (8 chars)
    "h": "7f3a2e8b...", # corpus/query hash (16 chars)
    "op": 3,          # operation code (3 = search)
    "d": 1,           # domain code (1 = sigils)
    "cb": "!node_123" # callback node
}
```

**Result notification (via mesh):**
```python
{
    "v": 1,
    "t": "res",
    "id": "ab12",
    "rh": "9e2c...",   # result hash (stored at gateway)
    "len": 1500,       # result size in bytes
    "s": "ok",         # status: ok, err, timeout
    "ttl": 86400       # stored for 24hr at gateway
}
```

#### Meshtastic Computation Patterns

| Pattern | Description | Via Mesh | Via IP |
|---|---|---|---|
| **Hash Reference** | Send references to pre-synced data, not data itself | Instruction (~200B) | Nothing (corpus pre-synced) |
| **Delegation** | Request computation on known data | Task ref (~200B) | Full result retrieval later |
| **Sensor Aggregation** | Edge nodes process locally, send only metadata/decisions | Alert (~100B) | Nothing |
| **Task Queue** | Mesh as durable task queue, actual data via IP when available | Coordination (~200B) | Task data + results |

#### Power Considerations

| Mode | Current (3.3V) | Battery Life (2500mAh) |
|---|---|---|
| Active TX | ~120mA | ~18 hours |
| Receive | ~40mA | ~60 hours |
| Sleep + periodic check (5min) | ~1mA avg | ~1 week |

Strategy: aggressive sleep/wake cycles. Send task request → sleep for estimated processing time → wake and check for response.

---

## Task Distribution

### Task Types

| Type | Description |
|---|---|
| **Parallel Inference** | Same query to multiple models, merge results |
| **Domain Routing** | Route query to specialized domain model on appropriate node |
| **Pipeline** | Sequential tasks with dependencies (DAG) |
| **Map-Reduce** | Split corpus search across nodes, aggregate findings |
| **Ensemble** | Generate multiple responses, select/blend best |

### Work Assignment Algorithm

1. **Capability matching:** Filter peers by task requirements (domain, context window, GPU).
2. **Load balancing:** Prefer nodes with lower current load.
3. **Model locality:** Prefer nodes with required model already loaded.
4. **Network proximity:** Prefer lowest latency; penalize remote/mesh peers.
5. **Geographic compliance:** Filter by geography if data sovereignty required.
6. **Fallback:** If no suitable peer, process locally.

**Scoring function (updated for hybrid network):**
```
score = (1 - cpu_percent) * 0.25
      + (1 - memory_percent) * 0.15
      + (model_loaded ? 1 : 0) * 0.30
      + network_score * 0.20
      + geo_match * 0.10

where network_score:
  local:  1.0
  remote: 0.5 (Cloudflare tunnel)
  mesh:   0.1 (Meshtastic gateway)
```

Assign task to highest-scoring peer. For latency-sensitive tasks (`max_latency_ms < 100`), filter to `local` peers only before scoring.

### Result Aggregation Strategies

- **First response:** Return first completed result (race).
- **Consensus:** Wait for majority, return most common.
- **Ensemble:** Collect all, blend/select best.
- **Reduce:** Custom reduction function.

## Communication Transport

- **Primary (local):** HTTP/2 with gRPC for low-latency RPC.
- **Remote (tunneled):** HTTPS via Cloudflare Tunnel endpoints.
- **Fallback:** HTTP/1.1 REST for compatibility.
- **Message queue:** NATS or Redis Pub/Sub for async task distribution.
- **Mesh (LoRa):** Meshtastic PRIVATE_APP portnum, msgpack encoding.

### Core Endpoints

```
POST /tasks/submit        # Submit task to node
GET  /tasks/{id}          # Query task status
POST /tasks/{id}/result   # Return completed result
GET  /peers               # List known peers
GET  /health              # Node health/capacity
POST /models/load         # Request model loading
```

All endpoints require Bearer token authentication (see Security section).

## Failure Handling

- **Timeout:** Task-level (default 300s). Unresponsive node → reassign to next-best. Max 3 retries before local fallback.
- **Node failure:** Heartbeat miss triggers peer removal. In-flight tasks redistributed.
- **Network partition:** Each partition operates independently. Merge on reconnect. No split-brain (no shared state).
- **Laptop sleep mid-task:** Timeout + reassignment. Coordinator auto-expires stale peers (120s TTL for Cloudflare, 90s for mDNS).
- **Gateway offline (Meshtastic):** Store-and-forward (mesh buffers message). Task retried when gateway comes back.
- **Permanent node loss:** After 3 failed heartbeats, removed from registry. Tasks degrade to remaining peers.

---

## Security: Ed25519 PKI Token System

Once DRM extends beyond trusted local network (Cloudflare Tunnels), proper authentication is mandatory. The system uses a two-layer token architecture based on Ed25519 public key cryptography.

### Layer 1: Mesh Membership (Long-Lived)

Each node has an Ed25519 keypair proving it's an authorized member of the mesh. Used for peer registration with the coordinator. Rotated monthly or on compromise.

**Key generation:**
```bash
polly keygen --name nas-polly
# Output: nas-polly.pub, nas-polly.key
# Node ID derived from public key: polly_7a8b9c...
```

**Mesh constitution (`trusted-peers.yaml`):**
```yaml
mesh_id: "polly-mesh-home"
version: 1

peers:
  - node_id: polly_7a8b9c
    name: nas-polly
    public_key: "AAAAC3NzaC1lZDI1NTE5AAAAIFqZ8b..."
    added: 2026-02-08
    roles: [worker, coordinator]

  - node_id: polly_3d4e5f
    name: desktop-polly
    public_key: "AAAAC3NzaC1lZDI1NTE5AAAAIGh3k2..."
    added: 2026-02-08
    roles: [worker]

  - node_id: polly_9g0h1i
    name: friend-server
    public_key: "AAAAC3NzaC1lZDI1NTE5AAAAIMn8pq..."
    added: 2026-02-09
    roles: [worker]
    max_concurrent_tasks: 5

revoked: []

signature: <ed25519 signature of above by mesh admin key>
```

Distributed to all nodes. All nodes verify signature against admin public key before accepting. Adding/removing peers requires admin re-sign and redistribution.

**Admin key:** Designated mesh administrator key. Keep offline (cold storage). Only used for mesh config updates. Consider multisig (2-of-3 admin keys) for critical meshes.

### Layer 2: Task Authorization (Short-Lived)

JWT-based with Ed25519 signatures (asymmetric — better for p2p than HMAC). Generated per request, valid 5 minutes.

**Token structure (JWT):**
```json
{
  "header": {
    "alg": "EdDSA",
    "typ": "JWT",
    "kid": "polly_7a8b9c"
  },
  "payload": {
    "iss": "polly_7a8b9c",
    "aud": "polly_3d4e5f",
    "sub": "task",
    "exp": 1707408120,
    "iat": 1707407820,
    "jti": "task_uuid_a1b2c3",
    "mesh": "polly-mesh-home",
    "claims": {
      "task_type": "domain_routing",
      "priority": "normal",
      "max_tokens": 2048
    }
  },
  "signature": "<ed25519 signature>"
}
```

**Verification flow (recipient):**
1. Decode header → get sender `kid` (node ID).
2. Look up sender's public key in `trusted-peers.yaml`.
3. Verify Ed25519 signature.
4. Check: `aud` matches self, `exp` not passed, `mesh` matches own mesh.
5. Check: `jti` (task ID) not in replay cache.
6. Check: sender has required role in peer config.

### Replay Protection

- Task ID bound to token (`jti` claim). Recipient tracks processed task IDs in memory with TTL matching token expiry.
- Timestamp validation: `iat` within ±5min clock skew.
- Short 5-minute expiry limits replay window.

### Token Rotation & Revocation

- **Mesh membership rotation:** Monthly keypair rotation. New key published to `trusted-peers.yaml`. Old key valid for 7-day grace period.
- **Emergency revocation:** Add node to `revoked` list in `trusted-peers.yaml`. Re-sign and distribute. All nodes reject tokens from revoked nodes immediately.
- **Task tokens:** No rotation needed (5-min expiry). If task exceeds 5min, recipient doesn't re-verify (task already started).

### Key Storage

```
~/.polly/keys/
  nas-polly.key          # chmod 600 (owner read/write only)
  nas-polly.pub          # chmod 644 (world readable)

~/.polly/drm/
  trusted-peers.yaml     # mesh constitution
  admin.pub              # admin public key for verification
```

Private keys never leave the node. Backup via GPG encryption to password manager.

### Simplified Alternative: Shared Secret

For small, fully-trusted meshes (2–5 nodes, all yours), HMAC-based shared secret is simpler:

```yaml
mesh_id: polly-mesh-home
shared_secret: "long-random-string-64-chars-minimum"
```

Tradeoffs: simpler implementation, faster symmetric crypto. But compromise affects entire mesh, can't revoke individual nodes, no non-repudiation.

**Recommendation:** Use Ed25519 PKI for any mesh that includes remote peers or semi-trusted nodes (friends' servers). Use shared secret only for local-only mesh during early development.

### Performance

| Operation | Time |
|---|---|
| Key generation | ~1ms (one-time) |
| Token creation (signing) | ~0.5ms |
| Token verification | ~0.8ms |
| Replay check (hash lookup) | ~0.1ms |
| **Total per-task overhead** | **~1.5ms** (negligible vs inference) |

---

## Configuration

```yaml
# polly-drm.yaml
node:
  name: "nas-polly"
  listen_port: 8765
  max_concurrent_tasks: 10

discovery:
  # Layer 1: Local
  mdns:
    enabled: true
    heartbeat_interval: 30s
    peer_timeout: 90s

  # Layer 2: Remote
  cloudflare:
    enabled: false
    coordinator_url: "https://polly-mesh.yourdomain.workers.dev"
    tunnel_url: "https://nas-polly.yourdomain.com"
    heartbeat_interval: 60s

  # Layer 3: Resilience
  meshtastic:
    enabled: false
    serial_port: "/dev/ttyUSB0"
    gateway_mode: false  # true if this node bridges mesh↔IP
    portnum: PRIVATE_APP

models:
  - domain: sigils
    model_id: llama3.2:3b-sigils-ft
    auto_load: true
    unload_after: 3600s

routing:
  strategy: score_based
  local_preference: 0.1
  max_retries: 3
  timeout_seconds: 300
  latency_sensitive_threshold_ms: 100  # below this, local peers only

resources:
  cpu_limit: 0.8
  memory_limit: 0.8
  reserve_cores: 2

networks:
  allowed_interfaces: ["en0", "tailscale0"]
  bind_address: "0.0.0.0"

security:
  # Phase 36: no auth (local trusted network)
  # Phase 36d+: Ed25519 PKI
  auth_method: none  # none | shared_secret | ed25519
  mesh_id: "polly-mesh-home"
  private_key: "~/.polly/keys/nas-polly.key"
  trusted_peers: "~/.polly/drm/trusted-peers.yaml"
  # Shared secret (simpler alternative)
  shared_secret: null
  # Rate limiting
  max_heartbeats_per_hour: 100
  max_tasks_per_hour: 1000
  max_concurrent_tasks_per_peer: 50

geography:
  country: "US"
  region: "us-east"
  enforce_data_sovereignty: false  # if true, tasks stay in same country
```

## Example Workflows

### Cross-Domain Analysis (Local)
```
Query: "Review this SuperCollider code for pedagogical clarity"
→ Break into: Code analysis (Sigils node) + Pedagogy extraction (Scrolls node) + Cross-reference (Glyphs node)
→ Parallel execution on 3 local nodes
→ Merge: combine technical + pedagogical + systemic insights
```

### Remote Model Specialization (Cloudflare)
```
NAS in Michigan receives query requiring Signals domain expertise.
NAS sees friend's server in California has signals-ft model loaded.
NAS sends task: POST https://friend-polly.theirdomain.com/tasks/submit
  (with Ed25519 JWT in Authorization header)
Friend's server processes, returns result through their tunnel.
Latency: ~100ms network + inference time. Negligible vs local for batch work.
```

### Off-Grid Research (Meshtastic)
```
Laptop in backcountry with Meshtastic radio. Gateway 20km away at base camp.
User needs species confirmation from knowledge corpus.
LoRa message: task request (~200 bytes) → gateway → IP → Polly mesh processes
LoRa response: result notification (~200 bytes)
Full result retrieved later when laptop regains WiFi.
```

### Large Corpus Search (Map-Reduce)
```
Query: "Find all references to 'finite games' in my corpus"
→ Map-reduce: Split corpus by domain/date → distribute to all peers (local + remote)
→ Remote peers accept batch work (latency-insensitive)
→ Aggregate and rank results → return top matches
```

## Relationship to Existing Systems

| System | Integration |
|---|---|
| **Agent Swarms** | DRM is the physical distribution layer for parallel agent tasks. Nexus composes logically; DRM distributes across nodes. Agent capability declarations map to DRM task requirements. See [agent-swarms spec](../agent-swarms/spec.md) |
| **Router** | DRM adds a node-routing tier above existing model/provider routing. Three-tier stack: Nexus (agents) → DRM (nodes) → Router v2 (models) |
| **LiteLLM** | A DRM peer is conceptually another "provider" — extends adapter pattern |
| **Query Decomposition (planned)** | Decomposed subtasks route across nodes via DRM |
| **RAG** | Distributed corpus search across node-local indices |
| **Mobile companion** | Mobile app is a thin DRM node (capture + chat relay). Connects via Cloudflare Tunnel when away from home network |
| **Security (Phase 23.5)** | Capability Broker concept extends to DRM node trust. Ed25519 PKI for inter-node authentication |
| **Observability (planned)** | Langfuse/Prometheus metrics per node, including network type and latency |

## Implementation Phases

### DRM Phase 1: Basic Peer Discovery (2–3 weeks) — Phase 36
- mDNS service announcement and peer registry
- Node capability manifests + health endpoint
- Manual task assignment API ("run this on node X")
- No authentication (trusted local network)

### DRM Phase 2: Automatic Distribution (3–4 weeks) — Phase 36a
- Task submission API with assignment algorithm
- Result collection and merging (first-response, consensus)
- Basic failure handling (timeout, retry, reassign)

### DRM Phase 3: Model Specialization (3–4 weeks) — Phase 36b
- Domain-aware routing across nodes
- Model loading coordination
- Parallel inference and ensemble generation
- Depends on: intelligent routing pipeline (Wave 3) complete

### DRM Phase 4: Advanced Features (4+ weeks) — Phase 36c
- Pipeline dependencies (DAG execution)
- Map-reduce corpus operations
- Adaptive load balancing + performance telemetry
- Mobile node support (join/leave gracefully)

### DRM Phase 5: Remote Mesh via Cloudflare (3–4 weeks) — Phase 36d
- `cloudflared` tunnel setup and management
- Cloudflare Workers coordination service (peer registry)
- Ed25519 PKI: key generation CLI, `trusted-peers.yaml` management
- JWT task authorization tokens
- Hybrid discovery (merge mDNS + Cloudflare peers)
- Network-type-aware scoring (local preference for latency-sensitive)
- Replay protection, token rotation, emergency revocation
- Geographic tagging and data sovereignty routing
- Depends on: Phase 36a (automatic distribution working locally first)

### DRM Phase 6: Meshtastic Gateway (2–3 weeks) — Phase 36e
- Meshtastic serial interface integration
- Gateway node software (bridge LoRa ↔ IP)
- Custom DRM message protocol (msgpack, dictionary encoding)
- Hash-reference computation pattern (coordinate, don't transfer)
- Store-and-forward for offline result retrieval
- Power-aware scheduling (sleep/wake cycles)
- Depends on: Phase 36a; independent of Cloudflare layer

## Performance Targets

| Metric | Local | Remote (CF) | Mesh (LoRa) |
|---|---|---|---|
| Peer discovery | <100ms | <500ms | N/A (gateway) |
| Task routing | <50ms | <50ms | N/A |
| Network transfer | 1–10ms | 50–150ms | 2–30s (coordination only) |
| Total overhead | <200ms | <400ms | Seconds (coordination) + later retrieval |
| Scale | 2–10 nodes | 2–20 nodes | 2–10 gateways |

## Monitoring

- **Prometheus metrics:** `polly_tasks_total`, `polly_task_duration_seconds`, `polly_peer_count`, `polly_model_load_time_seconds`, `polly_resource_usage`, `polly_network_type` (per-task breakdown: local/remote/mesh)
- **Structured JSON logs:** Peer discovery, task assignment, model loading, failures, token verification events.
- **Optional dashboard:** Active peer topology (with network type overlay), task distribution heatmap, resource utilization, geographic map of mesh nodes.

## Storage

- `~/.polly/drm/` — Node identity, peer registry cache, task queue (SQLite), `trusted-peers.yaml`.
- `~/.polly/keys/` — Ed25519 keypairs (private key chmod 600).
- DRM state separate from main Polly data to allow clean enable/disable.

## The Autonomist Frame

**Cloudflare as infrastructure, not dependency:** You're using Cloudflare's roads, not renting their houses. Compute stays on your hardware. If Cloudflare disappeared, you fall back to local mesh + Tailscale. Coordination logic is simple enough to self-host.

**Meshtastic as post-internet computing:** When centralized infrastructure fails — disaster, censorship, outage — the mesh persists. Resilient, local-first, commons-based, low-power, censorship-resistant. Solar-sustainable. Computation becomes mutual aid via radio waves.

**Federation model:** Each node has sovereignty. Cluster emerges from voluntary participation. Analogous to email: run your own server, use common protocol, interoperate through neutral infrastructure. No platform lock-in.

## Reference

- Implementation: `core/drm/` (planned)
- Config: `config/polly-drm.yaml` (planned)
- Keys: `~/.polly/keys/`, `~/.polly/drm/trusted-peers.yaml`
- Existing router: `core/router.py`, `core/router_v2.py`
- LiteLLM adapter: `core/providers/litellm_adapter.py`
- Agent Swarms: [agent-swarms spec](../agent-swarms/spec.md)
- Security: [security spec](../security/spec.md)
- Change folder: [openspec/changes/spec-integration-2026-02/](../../changes/spec-integration-2026-02/)
