'use client';

import { generateSecretKey, getPublicKey, finalizeEvent, SimplePool, nip19 } from 'nostr-tools';

const RELAYS = [
  'wss://relay.damus.io',
  'wss://nos.lol',
  'wss://relay.primal.net',
  'wss://nostr.wine',
];

const NSEC_KEY = 'nostr_nsec';
const BROADCAST_KEY = 'nostr_broadcast_enabled';
export const NPUB_TOAST_SESSION_KEY = 'nostr_npub_shown';

export type NostrKeypair = {
  nsec: string;
  npub: string;
};

export function getOrCreateNostrKeypair(): NostrKeypair & { secretKey: Uint8Array; publicKey: string } {
  const stored = localStorage.getItem(NSEC_KEY);
  let secretKey: Uint8Array;

  if (stored && nip19.NostrTypeGuard.isNSec(stored)) {
    const decoded = nip19.decode(stored);
    secretKey = decoded.data as Uint8Array;
  } else {
    secretKey = generateSecretKey();
    const nsec = nip19.nsecEncode(secretKey);
    localStorage.setItem(NSEC_KEY, nsec);
  }

  const publicKey = getPublicKey(secretKey);
  const npub = nip19.npubEncode(publicKey);
  const nsec = nip19.nsecEncode(secretKey);
  return { nsec, npub, secretKey, publicKey };
}

export function isBroadcastEnabled(): boolean {
  const stored = localStorage.getItem(BROADCAST_KEY);
  return stored === null ? true : stored === 'true';
}

export function setBroadcastEnabled(enabled: boolean): void {
  localStorage.setItem(BROADCAST_KEY, String(enabled));
}

export const broadcastDeedEvent = async (
  type: 'signal' | 'verify' | 'scar' | 'recovery' | 'recovery_approved' | 'recovery_rejected',
  deedId: string,
  content: string,
  extraTags?: string[][]
): Promise<boolean> => {
  if (!isBroadcastEnabled()) return false;

  try {
    const { secretKey } = getOrCreateNostrKeypair();

    const tags: string[][] = [
      ['t', 'deedledger'],
      ['t', 'reputation'],
      ['d', deedId],
      ['deed-type', type],
      ...(extraTags ?? []),
    ];

    const event = finalizeEvent(
      {
        kind: 1,
        created_at: Math.floor(Date.now() / 1000),
        tags,
        content,
      },
      secretKey
    );

    const pool = new SimplePool();
    await Promise.any(pool.publish(RELAYS, event));
    console.log(`Nostr event published: https://njump.me/${event.id}`);
    pool.close(RELAYS);
    return true;
  } catch (e) {
    if (e instanceof AggregateError) {
      console.warn('Nostr broadcast failed on all relays (silent):', e.errors);
    } else {
      console.warn('Nostr broadcast failed (silent):', e);
    }
    return false;
  }
};
