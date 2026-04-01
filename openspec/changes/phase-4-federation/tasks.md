# Phase 4: Federation

**Status:** 💡 Future — not started  
**Gate:** Phase 3 complete  
**Spec sources:** `DISTRIBUTED_NODES.md`, `FEDERATED_COLLABORATION.md`, `POLLY_WEB_ANALYSIS.md`

## Goal

Multiple OpenClaw nodes collaborating. PicoClaw (Raspberry Pi) as a lightweight satellite node. Cross-instance Liaison protocol for multi-user agent sessions. Extended to include household device mesh: NAS compute node, Android always-on node, mobile relay pattern, and the household compute mesh vision (Reading A of the Polly Web).

---

## Household Compute Mesh (Reading A — spec this phase)

*Source: `POLLY_WEB_ANALYSIS.md` §2, §4*

The gateway orchestrates a home-network compute mesh. Brett's Mac Mini remains the center. Household devices contribute what they're actually good at — not a theoretical always-on inference farm, but honest capability-matched contribution.

### New Node Classes (extend `DISTRIBUTED_NODES.md`)

Three node classes to add to the capability registry beyond PicoClaw:

**`android-always-on`** — plugged-in Android devices (Apolosign, NAS-attached displays) that register via mDNS and accept dispatched workloads. Same registration protocol as PicoClaw, running Android instead of custom OS. Target capabilities: BGE-small (embedding), Kokoro (TTS), Phi-3-mini (lightweight inference).

**`nas-docker`** — NAS running Ollama in a Docker container. Registers via mDNS. Target hardware: UGREEN NASync DXP4800 (ARM Cortex-A55, 16GB RAM). Capabilities: inference (7B range at 4-bit), embedding, vector store persistence. NAS is always-on, LAN-connected, Docker-ready — this is a Docker run command + registration agent, not a research project.

**`mobile-relay`** — phones (iOS or Android) that process on-device for their own sessions only. Not dispatched to by the gateway as general workers. Sub-variants: `ios-relay`, `android-relay`. Capabilities declared but gated to `scope: self` only. Mobile devices cannot reliably run background inference — iOS kills processes; battery drain is prohibitive.

### Capability Registry Extensions (@backend)
- [ ] Register `android-always-on` node class in capability registry — mDNS registration, workload dispatch, capability match
- [ ] Register `nas-docker` node class — Docker container running Ollama + registration agent on ARM64 NAS
- [ ] Register `mobile-relay` node class — capabilities declared, `scope: self` enforcement (not general dispatch targets)
- [ ] Android mDNS registration agent — small process that runs on Android devices, advertises capabilities via mDNS, accepts gateway-dispatched workloads (PicoClaw protocol on Android OS)
- [ ] Docker-based registration agent spec for NAS — `docker run` command + Ollama + mDNS advertisement + workload executor

### Charging-Aware Mobile Embedding Queue (@backend + @infra)
- [ ] Mobile devices accumulate content (voice captures, typed notes) that benefits from embedding
- [ ] While charging + idle: device processes local embedding queue, syncs vectors to gateway
- [ ] While on battery: defer all embedding queue processing
- [ ] Architecturally consistent with Knowledge Skill's dirty-flag watcher cycle — mobile device is an additional content source with deferred indexing
- [ ] Mobile contribution consent: **Settings only, default off** — not in onboarding (too complex). Setting: "Contribute processing when charging." 
- [ ] @infra: charging state detection + queue pause/resume logic

### NAS as Compute Node — Priority Task
- [ ] Docker container: Ollama on ARM64 + PicoClaw-protocol registration agent
- [ ] Capability advertisement: inference (7B range), embedding, vector store persistence candidate
- [ ] Gateway routing: prefer Mac Mini for latency-sensitive; route to NAS for batch embedding, background indexing
- [ ] Open question (Q1 from `POLLY_WEB_ANALYSIS.md`): should FAISS index live on NAS storage (high capacity, persistent) rather than Mac Mini (low latency)? Decision depends on vault size and update/query ratio. @backend to evaluate when phase begins — document in `KNOWLEDGE_SKILL.md`.

### Apolosign as Embedding/TTS Node
- [ ] Register Apolosign (RK3576, always-on, LAN-connected) as `android-always-on` node
- [ ] Capabilities: BGE-small (embedding), Kokoro (TTS), Phi-3-mini (lightweight inference)
- [ ] This is the highest-value Android compute node in the current hardware setup — plugged in, no battery constraint

---

## Polly Web Forward Spec (POLLY_WEB.md)

*Source: `POLLY_WEB_ANALYSIS.md` §4, §5.3*

- [ ] Write `POLLY_WEB.md` as a forward-spec document covering:
  - Reading A (household mesh) in implementation detail — extends `DISTRIBUTED_NODES.md`
  - NAS compute node setup (Docker + Ollama + mDNS)
  - Charging-aware mobile embedding queue
  - Reading B (voluntary peer network) as a future horizon: what it would require (trust model, contribution accounting, privacy guarantees for queries routed to unknown hardware)
  - Explicit decision: Reading C (public mesh / BOINC-style) is **out of scope for the foreseeable future**
  - Note: `FEDERATED_COLLABORATION.md` git mailbox could theoretically carry compute tasks for Reading B peer networks — trust model underdeveloped, flag for future spec

---

## PicoClaw + Liaison (original scope)

- [ ] `DISTRIBUTED_NODES.md` — PicoClaw node architecture, full mDNS registration + sync protocol
- [ ] `FEDERATED_COLLABORATION.md` — cross-instance Liaison protocol, multi-user federated sessions
- [ ] Populate remaining tasks when Phase 3 is shipping

---

## Done When
NAS registered as `nas-docker` compute node. Apolosign registered as `android-always-on` node. Mobile relay pattern specced. `POLLY_WEB.md` written. PicoClaw + Liaison tasks fully populated (gate: Phase 3 shipping).
