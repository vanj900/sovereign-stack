'use client'

import { useState, useEffect, useRef } from 'react'
import { SimplePool, type Filter } from 'nostr-tools'

interface DeedEvent {
  id: string
  type: string
  description: string
  timestamp: string
  controller: string
  source?: 'ghost' | 'local'
}

const GHOST_DEED_RELAYS = (
  process.env.NEXT_PUBLIC_NOSTR_RELAYS?.split(',') ?? [
    'wss://relay.damus.io',
    'wss://nos.lol',
  ]
).filter(Boolean)

const GHOST_DEED_TYPES = ['ghost_adapt', 'ghost_reflect'] as const

export default function EventLog() {
  const [events, setEvents] = useState<DeedEvent[]>([])
  const poolRef = useRef<SimplePool | null>(null)

  useEffect(() => {
    // Seed with mock events until live Nostr data arrives
    const mockEvents: DeedEvent[] = [
      {
        id: '1',
        type: 'signal_sent',
        description: 'Initial signal uploaded',
        timestamp: new Date(Date.now() - 86400000).toISOString(),
        controller: 'did:key:z6Mk...',
        source: 'local',
      },
      {
        id: '2',
        type: 'deed_completed',
        description: 'Code review completed for project X',
        timestamp: new Date(Date.now() - 43200000).toISOString(),
        controller: 'did:key:z6Mk...',
        source: 'local',
      },
    ]
    setEvents(mockEvents)

    // Subscribe to Ghost deed receipts on Nostr (kind 30023, ghost_adapt / ghost_reflect)
    const pool = new SimplePool()
    poolRef.current = pool

    const sub = pool.subscribeMany(
      GHOST_DEED_RELAYS,
      { kinds: [30023], '#t': [...GHOST_DEED_TYPES] } as Filter,
      {
        onevent(nostrEvent) {
          const typeTag = nostrEvent.tags.find((t) => t[0] === 't')
          const deedType = typeTag?.[1] ?? 'ghost_adapt'
          setEvents((prev) => {
            // De-duplicate by Nostr event id
            if (prev.some((e) => e.id === nostrEvent.id)) return prev
            return [
              {
                id: nostrEvent.id,
                type: deedType,
                description: nostrEvent.content,
                timestamp: new Date(nostrEvent.created_at * 1000).toISOString(),
                controller: nostrEvent.pubkey,
                source: 'ghost',
              },
              ...prev,
            ]
          })
        },
      }
    )

    return () => {
      sub.close()
      pool.close(GHOST_DEED_RELAYS)
      poolRef.current = null
    }
  }, [])

  const getEventColor = (type: string) => {
    switch (type) {
      case 'signal_sent': return 'bg-blue-100 text-blue-800'
      case 'deed_completed': return 'bg-green-100 text-green-800'
      case 'vouch': return 'bg-purple-100 text-purple-800'
      case 'dispute': return 'bg-red-100 text-red-800'
      case 'ghost_adapt': return 'bg-violet-100 text-violet-800'
      case 'ghost_reflect': return 'bg-indigo-100 text-indigo-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-3">
      {events.length === 0 ? (
        <p className="text-sm text-gray-500 text-center py-8">
          No events yet. Connect your DID and submit a signal to get started.
        </p>
      ) : (
        events.map((event) => (
          <div
            key={event.id}
            className="flex items-start gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <span className={`px-2 py-1 rounded text-xs font-medium ${getEventColor(event.type)}`}>
              {event.type}
            </span>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900">
                {event.description}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {new Date(event.timestamp).toLocaleString()}
                {event.source === 'ghost' && (
                  <span className="ml-2 text-violet-500">• Ghost</span>
                )}
              </p>
            </div>
          </div>
        ))
      )}
    </div>
  )
}

