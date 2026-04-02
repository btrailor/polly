/**
 * pollyObservationStore unit tests
 * Covers: observation state machine, dismissal persistence, T3 auto-resolve,
 *         subscriptions, idempotency, terminal state guarantee
 */

// Reset module state between tests (the store uses module-level variables)
beforeEach(() => {
  jest.resetModules();
  jest.clearAllMocks();
});

const BASE_OBS = {
  id: 'obs-001',
  triggerType: 'T1' as const,
  observationText: "You've been in the same task for 4 hours.",
  actionType: null as const,
};

function getStore() {
  return require('../../src/store/pollyObservationStore');
}

describe('pollyObservationStore — state machine', () => {
  it('enqueueObservation: adds observation in QUEUED state', async () => {
    const store = getStore();
    await store.initPollyStore();
    store.enqueueObservation(BASE_OBS);

    // No active yet if no prior observations — first queued should be promoted to active
    const active = store.getActiveObservation();
    expect(active).not.toBeNull();
    expect(active?.id).toBe('obs-001');
    expect(active?.state).toBe('active');
  });

  it('enqueueObservation: is idempotent (duplicate id is dropped)', async () => {
    const store = getStore();
    await store.initPollyStore();
    store.enqueueObservation(BASE_OBS);
    store.enqueueObservation(BASE_OBS); // duplicate

    const active = store.getActiveObservation();
    expect(active?.id).toBe('obs-001');
  });

  it('engageObservation: transitions active → engaged', async () => {
    const store = getStore();
    await store.initPollyStore();
    store.enqueueObservation(BASE_OBS);

    store.engageObservation('obs-001');
    const active = store.getActiveObservation();
    expect(active?.state).toBe('engaged');
    expect(typeof active?.engagedAt).toBe('number');
  });

  it('engageObservation: no-op if observation not in active state', async () => {
    const store = getStore();
    await store.initPollyStore();
    store.enqueueObservation(BASE_OBS);
    store.engageObservation('obs-001'); // → engaged
    store.engageObservation('obs-001'); // already engaged, no change
    expect(store.getActiveObservation()?.state).toBe('engaged');
  });

  it('dismissObservation: transitions to dismissed (terminal)', async () => {
    const store = getStore();
    await store.initPollyStore();
    store.enqueueObservation(BASE_OBS);
    store.dismissObservation('obs-001');

    expect(store.getActiveObservation()).toBeNull();
  });

  it('dismissObservation: is idempotent (double dismiss is safe)', async () => {
    const store = getStore();
    await store.initPollyStore();
    store.enqueueObservation(BASE_OBS);
    store.dismissObservation('obs-001');
    expect(() => store.dismissObservation('obs-001')).not.toThrow();
  });

  it('dismissObservation: promotes next queued to active', async () => {
    const store = getStore();
    await store.initPollyStore();
    store.enqueueObservation({ ...BASE_OBS, id: 'obs-001' });
    store.enqueueObservation({ ...BASE_OBS, id: 'obs-002' });

    // obs-001 should be active, obs-002 queued
    expect(store.getActiveObservation()?.id).toBe('obs-001');

    store.dismissObservation('obs-001');
    // obs-002 should now be active
    expect(store.getActiveObservation()?.id).toBe('obs-002');
    expect(store.getActiveObservation()?.state).toBe('active');
  });

  it('getActiveObservation: returns null when no observations', async () => {
    const store = getStore();
    await store.initPollyStore();
    expect(store.getActiveObservation()).toBeNull();
  });
});

describe('pollyObservationStore — T3 auto-resolve', () => {
  it('autoResolveT3: dismisses a T3 observation automatically', async () => {
    const store = getStore();
    await store.initPollyStore();
    store.enqueueObservation({ ...BASE_OBS, id: 't3-obs', triggerType: 'T3' as const });

    store.autoResolveT3('t3-obs');
    expect(store.getActiveObservation()).toBeNull();
  });

  it('autoResolveT3: no-op on non-T3 observations', async () => {
    const store = getStore();
    await store.initPollyStore();
    store.enqueueObservation({ ...BASE_OBS, id: 't1-obs', triggerType: 'T1' as const });

    store.autoResolveT3('t1-obs'); // should not dismiss T1
    expect(store.getActiveObservation()?.id).toBe('t1-obs');
  });

  it('autoResolveT3: no-op if already dismissed', async () => {
    const store = getStore();
    await store.initPollyStore();
    store.enqueueObservation({ ...BASE_OBS, id: 't3-obs', triggerType: 'T3' as const });
    store.dismissObservation('t3-obs');
    expect(() => store.autoResolveT3('t3-obs')).not.toThrow();
  });
});

describe('pollyObservationStore — terminal state guarantee', () => {
  it('previously dismissed ID cannot be re-queued', async () => {
    const store = getStore();
    await store.initPollyStore();
    store.enqueueObservation(BASE_OBS);
    store.dismissObservation('obs-001');

    // Try to re-enqueue
    store.enqueueObservation(BASE_OBS);
    expect(store.getActiveObservation()).toBeNull();
  });
});

describe('pollyObservationStore — subscriptions', () => {
  it('subscriber is notified on enqueue', async () => {
    const store = getStore();
    await store.initPollyStore();
    const listener = jest.fn();
    store.subscribeToPollyStore(listener);

    store.enqueueObservation(BASE_OBS);
    expect(listener).toHaveBeenCalled();
  });

  it('subscriber is notified on dismiss', async () => {
    const store = getStore();
    await store.initPollyStore();
    store.enqueueObservation(BASE_OBS);

    const listener = jest.fn();
    store.subscribeToPollyStore(listener);
    store.dismissObservation('obs-001');
    expect(listener).toHaveBeenCalled();
  });

  it('unsubscribe stops notifications', async () => {
    const store = getStore();
    await store.initPollyStore();
    const listener = jest.fn();
    const unsub = store.subscribeToPollyStore(listener);

    unsub();
    store.enqueueObservation(BASE_OBS);
    expect(listener).not.toHaveBeenCalled();
  });
});

describe('pollyObservationStore — initPollyStore', () => {
  it('is idempotent — double init is safe', async () => {
    const store = getStore();
    await store.initPollyStore();
    await expect(store.initPollyStore()).resolves.not.toThrow();
  });
});
