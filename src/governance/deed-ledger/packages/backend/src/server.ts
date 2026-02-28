import { createServer, IncomingMessage, ServerResponse } from 'node:http';
import { finalizeEvent } from 'nostr-tools';
import { nip19 } from 'nostr-tools';
import type { EventTemplate } from 'nostr-tools';
import { NostrClient } from './nostr.js';

const PORT = parseInt(process.env.GHOST_DEED_PORT ?? '3001', 10);
if (isNaN(PORT) || PORT < 1 || PORT > 65535) {
  throw new Error(
    `[deed-ledger] GHOST_DEED_PORT is invalid: "${process.env.GHOST_DEED_PORT}". ` +
      'Must be an integer between 1 and 65535.'
  );
}

// ── Parse incoming request body ───────────────────────────────────────────────
function readBody(req: IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', (chunk: Buffer) => { data += chunk.toString(); });
    req.on('end', () => resolve(data));
    req.on('error', reject);
  });
}

// ── POST /ghost-deed handler ──────────────────────────────────────────────────
// Accepts an unsigned Ghost deed event JSON, signs it with the backend Nostr
// key (NOSTR_NSEC), and publishes it to configured relays via NostrClient.
export async function handleGhostDeed(
  req: IncomingMessage,
  res: ServerResponse
): Promise<void> {
  if (req.method !== 'POST') {
    res.writeHead(405, { Allow: 'POST' }).end('Method Not Allowed');
    return;
  }

  let bodyText: string;
  try {
    bodyText = await readBody(req);
  } catch {
    res.writeHead(400).end('Bad Request: could not read body');
    return;
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let deedJson: Record<string, any>;
  try {
    deedJson = JSON.parse(bodyText);
  } catch {
    res.writeHead(400).end('Bad Request: invalid JSON');
    return;
  }

  const nsec = process.env.NOSTR_NSEC;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let event: Record<string, any>;

  if (nsec) {
    try {
      const decoded = nip19.decode(nsec);
      if (decoded.type !== 'nsec') {
        throw new Error(`Expected nsec, got ${decoded.type}`);
      }
      const secretKey = decoded.data as Uint8Array;

      // Validate required fields before passing to nostr-tools
      const tags = deedJson.tags;
      if (!Array.isArray(tags)) {
        res.writeHead(400).end('Bad Request: "tags" must be an array');
        return;
      }

      const template: EventTemplate = {
        kind: (deedJson.kind as number) ?? 30023,
        created_at: (deedJson.created_at as number) ?? Math.floor(Date.now() / 1000),
        tags: tags as string[][],
        content: (deedJson.content as string) ?? '',
      };
      const signed = finalizeEvent(template, secretKey);
      console.log(
        `[ghost-deed] signed event id=${signed.id}  pubkey=${signed.pubkey.slice(0, 8)}…`
      );
      event = signed as unknown as Record<string, unknown>;
    } catch (err) {
      console.error('[ghost-deed] signing failed (check NOSTR_NSEC configuration):', err);
      res.writeHead(500).end('Internal Server Error: deed signing failed');
      return;
    }
  } else {
    console.warn('[ghost-deed] NOSTR_NSEC not set — publishing unsigned stub');
    event = deedJson;
  }

  const nostr = new NostrClient();
  await nostr.publishEvent(event as Parameters<NostrClient['publishEvent']>[0]);

  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ ok: true, id: (event.id as string) ?? null }));
}

// ── HTTP server ───────────────────────────────────────────────────────────────
export function startServer(): void {
  const server = createServer((req, res) => {
    if (req.url === '/ghost-deed') {
      handleGhostDeed(req, res).catch((err) => {
        console.error('[ghost-deed] unhandled error:', err);
        if (!res.headersSent) {
          res.writeHead(500).end('Internal Server Error');
        }
      });
    } else {
      res.writeHead(404).end('Not Found');
    }
  });

  server.listen(PORT, () => {
    console.log(
      `[deed-ledger] ghost-deed ingest endpoint listening on http://localhost:${PORT}/ghost-deed`
    );
  });
}

// Auto-start when this file is the entry point
// Works with: tsx src/server.ts  (see npm run dev / npm start)
startServer();
