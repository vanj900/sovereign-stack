'use client'

import { useState, useEffect } from 'react'

interface ScarSummary {
  deedId: string
  scarNote: string
  createdAt: string
  recoveryStatus?: 'pending' | 'approved' | 'rejected'
}

interface InfluenceStats {
  totalScore: number
  deedCount: number
  status: string
  decayRate: number
  scars: ScarSummary[]
}

export default function InfluenceDashboard() {
  const [stats, setStats] = useState<InfluenceStats>({
    totalScore: 0,
    deedCount: 0,
    status: 'invite_pending',
    decayRate: 0.05,
    scars: [],
  })

  useEffect(() => {
    // Stub: In production, fetch from Ceramic
    setStats({
      totalScore: 42.5,
      deedCount: 3,
      status: 'observer',
      decayRate: 0.05,
      scars: [
        {
          deedId: 'example-deed-id-1',
          scarNote: 'Disputed: incomplete deliverable',
          createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          recoveryStatus: undefined,
        },
      ],
    })
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'node': return 'text-green-700 bg-green-100'
      case 'observer': return 'text-blue-700 bg-blue-100'
      case 'signal_sent': return 'text-yellow-700 bg-yellow-100'
      default: return 'text-gray-700 bg-gray-100'
    }
  }

  const getRecoveryBadge = (status?: ScarSummary['recoveryStatus']) => {
    switch (status) {
      case 'pending': return <span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">⏳ Recovery pending</span>
      case 'approved': return <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700">✅ Recovery approved</span>
      case 'rejected': return <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700">❌ Recovery rejected</span>
      default: return null
    }
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center">
          <p className="text-3xl font-bold text-trust-600">
            {stats.totalScore.toFixed(1)}
          </p>
          <p className="text-sm text-gray-600 mt-1">Total Score</p>
        </div>
        
        <div className="text-center">
          <p className="text-3xl font-bold text-gray-900">
            {stats.deedCount}
          </p>
          <p className="text-sm text-gray-600 mt-1">Deeds</p>
        </div>
        
        <div className="text-center">
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(stats.status)}`}>
            {stats.status}
          </span>
          <p className="text-sm text-gray-600 mt-1">Status</p>
        </div>
        
        <div className="text-center">
          <p className="text-3xl font-bold text-orange-600">
            {(stats.decayRate * 100).toFixed(1)}%
          </p>
          <p className="text-sm text-gray-600 mt-1">Decay Rate</p>
        </div>
      </div>

      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-sm text-yellow-800">
          ⚠️ <strong>Demurrage active:</strong> Your influence decays {(stats.decayRate * 100).toFixed(1)}% per week without contribution.
          Complete deeds or verify others&apos; work to maintain reputation.
        </p>
      </div>

      {stats.scars.length > 0 && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg space-y-3">
          <p className="text-sm font-semibold text-red-800">🩸 Active Scars ({stats.scars.length})</p>
          {stats.scars.map((scar) => (
            <div key={scar.deedId} className="flex items-start justify-between gap-3 text-sm">
              <div className="flex-1">
                <p className="text-red-700">{scar.scarNote}</p>
                <p className="text-red-400 text-xs mt-0.5">
                  {new Date(scar.createdAt).toLocaleDateString()}
                </p>
              </div>
              <div className="flex flex-col items-end gap-1">
                {getRecoveryBadge(scar.recoveryStatus)}
                {!scar.recoveryStatus && (
                  <a
                    href="#scar-recovery"
                    className="text-xs px-2 py-0.5 rounded-full bg-amber-600 text-white hover:bg-amber-500 transition"
                  >
                    🩹 Submit Recovery
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
