'use client'

import { useEffect, useState } from 'react'
import { useDIDAuth } from '../../context/DIDContext'
import { getOrCreateNostrKeypair, isBroadcastEnabled, setBroadcastEnabled, NPUB_TOAST_SESSION_KEY } from '../lib/nostr'

export default function DIDConnect() {
  const { did, isAuthenticated, loading, loginWithKeypair, loginWithWallet, logout, address } = useDIDAuth()
  const [npub, setNpub] = useState<string | null>(null)
  const [npubToast, setNpubToast] = useState<string | null>(null)
  const [broadcastEnabled, setBroadcastEnabledState] = useState(true)

  // On mount, restore broadcast preference
  useEffect(() => {
    setBroadcastEnabledState(isBroadcastEnabled())
  }, [])

  // After DID connects, generate/load Nostr keypair and show npub toast once
  useEffect(() => {
    if (!isAuthenticated) return
    const kp = getOrCreateNostrKeypair()
    setNpub(kp.npub)
    // Only show toast if this is a new keypair (npub not previously shown in this session)
    const shown = sessionStorage.getItem(NPUB_TOAST_SESSION_KEY)
    if (!shown) {
      setNpubToast(kp.npub)
      sessionStorage.setItem(NPUB_TOAST_SESSION_KEY, '1')
    }
  }, [isAuthenticated])

  const handleBroadcastToggle = () => {
    const next = !broadcastEnabled
    setBroadcastEnabledState(next)
    setBroadcastEnabled(next)
  }

  return (
    <div className="space-y-4">
      {npubToast && (
        <div className="p-3 bg-yellow-50 rounded border border-yellow-300 flex justify-between items-start">
          <div>
            <p className="text-xs font-semibold text-yellow-800 mb-1">Your Nostr npub for broadcasting:</p>
            <p className="text-xs font-mono text-yellow-700 break-all">{npubToast}</p>
          </div>
          <button onClick={() => setNpubToast(null)} className="ml-2 text-yellow-600 text-sm">✕</button>
        </div>
      )}

      {!isAuthenticated ? (
        <>
          <p className="text-sm text-gray-600">
            Connect your DID to interact with the reputation ledger.
          </p>
          <button
            onClick={loginWithKeypair}
            disabled={loading}
            className="btn btn-primary w-full disabled:opacity-50"
          >
            {loading ? 'Connecting...' : '🔑 Login with Pure Keypair (recommended)'}
          </button>
          <button
            onClick={loginWithWallet}
            disabled={loading}
            className="btn btn-secondary w-full disabled:opacity-50"
          >
            {loading ? 'Connecting...' : '💰 Connect Wallet (did:pkh)'}
          </button>
          <p className="text-xs text-gray-500">
            Keypair: sovereign, effort-based, no third-party required.
          </p>
        </>
      ) : (
        <>
          <div className="p-3 bg-trust-50 rounded border border-trust-200">
            <p className="text-xs font-semibold text-trust-700 mb-1">Connected DID</p>
            <p className="text-xs font-mono text-trust-800 break-all">
              {did?.id}
            </p>
            {address && (
              <p className="text-xs text-trust-600 mt-1">
                Wallet: {address.slice(0, 6)}…{address.slice(-4)}
              </p>
            )}
            {npub && (
              <p className="text-xs text-trust-600 mt-1 font-mono break-all">
                npub: {npub.slice(0, 16)}…
              </p>
            )}
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded border border-gray-200">
            <span className="text-sm text-gray-700">Broadcast deeds to Nostr</span>
            <button
              onClick={handleBroadcastToggle}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${broadcastEnabled ? 'bg-trust-600' : 'bg-gray-300'}`}
              aria-label="Toggle Nostr broadcasting"
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${broadcastEnabled ? 'translate-x-6' : 'translate-x-1'}`}
              />
            </button>
          </div>
          <button
            onClick={logout}
            className="btn btn-secondary w-full"
          >
            Disconnect
          </button>
        </>
      )}
    </div>
  )
}
