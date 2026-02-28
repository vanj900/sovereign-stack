import type { Event } from 'nostr-tools';
import { SimplePool } from 'nostr-tools';

const DEFAULT_RELAYS = [
  'wss://relay.damus.io',
  'wss://nos.lol',
  'wss://relay.nostr.band'
];

export class NostrClient {
  private relayUrls: string[];

  constructor(relayUrls?: string[]) {
    this.relayUrls = relayUrls || 
      (process.env.NOSTR_RELAYS?.split(',') || DEFAULT_RELAYS);
  }

  async connect(): Promise<void> {
    console.log(`[nostr] Relay targets: ${this.relayUrls.join(', ')}`);
  }

  async publishEvent(event: Event): Promise<void> {
    console.log(`[nostr] Publishing event id=${(event.id || '(unsigned)').slice(0, 12)}…`);
    const pool = new SimplePool();
    try {
      await Promise.any(pool.publish(this.relayUrls, event));
      console.log('[nostr] Event published to at least one relay');
    } catch (err) {
      // AggregateError means all relays failed — treat as non-fatal
      if (err instanceof AggregateError) {
        console.warn('[nostr] All relays rejected the event (non-fatal)');
      } else {
        console.warn('[nostr] Relay publish failed (non-fatal):', err);
      }
    } finally {
      pool.close(this.relayUrls);
    }
  }

  async subscribeToEvents(
    filters: Parameters<SimplePool['subscribeMany']>[1],
    onEvent: (event: Event) => void
  ): Promise<() => void> {
    console.log('[nostr] Subscribing with filter:', filters);
    const pool = new SimplePool();
    const sub = pool.subscribeMany(this.relayUrls, filters, { onevent: onEvent });
    return () => {
      sub.close();
      pool.close(this.relayUrls);
    };
  }

  disconnect(): void {
    console.log('[nostr] Disconnected');
  }
}

// Helper to create a deed announcement event
export function createDeedEvent(
  deed: { id: string; type: string; description?: string },
  privateKey: string
): Event {
  // This is a stub - in production, properly sign with nostr-tools
  return {
    kind: 30023, // Long-form content kind for deeds
    created_at: Math.floor(Date.now() / 1000),
    tags: [
      ['d', deed.id],
      ['t', deed.type],
    ],
    content: deed.description || '',
    pubkey: '', // Would be derived from privateKey
    id: '', // Would be computed
    sig: '' // Would be signed
  };
}

