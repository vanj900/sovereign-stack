'use client'

import { useState, useEffect } from 'react'

interface DeedEvent {
  id: string
  type: string
  description: string
  timestamp: string
  controller: string
}

export default function EventLog() {
  const [events, setEvents] = useState<DeedEvent[]>([])

  useEffect(() => {
    // Stub: In production, fetch from Ceramic/Supabase
    const mockEvents: DeedEvent[] = [
      {
        id: '1',
        type: 'signal_sent',
        description: 'Initial signal uploaded',
        timestamp: new Date(Date.now() - 86400000).toISOString(),
        controller: 'did:key:z6Mk...'
      },
      {
        id: '2',
        type: 'deed_completed',
        description: 'Code review completed for project X',
        timestamp: new Date(Date.now() - 43200000).toISOString(),
        controller: 'did:key:z6Mk...'
      },
    ]
    setEvents(mockEvents)
  }, [])

  const getEventColor = (type: string) => {
    switch (type) {
      case 'signal_sent': return 'bg-blue-100 text-blue-800'
      case 'deed_completed': return 'bg-green-100 text-green-800'
      case 'vouch': return 'bg-purple-100 text-purple-800'
      case 'dispute': return 'bg-red-100 text-red-800'
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
              </p>
            </div>
          </div>
        ))
      )}
    </div>
  )
}
