'use client'

import { useState } from 'react'
import { sha256 } from '@noble/hashes/sha256'
import { bytesToHex } from '@noble/hashes/utils'
import { useDIDAuth } from '../../context/DIDContext'
import { composeClient } from '../../lib/ceramic'
import { broadcastDeedEvent } from '../lib/nostr'

export default function SignalUpload() {
  const { isAuthenticated, loginWithKeypair } = useDIDAuth()
  const [signal, setSignal] = useState('')
  const [hash, setHash] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isAuthenticated) return
    setIsSubmitting(true)
    setError(null)

    try {
      // Create hash proof
      const hashBytes = sha256(new TextEncoder().encode(signal))
      const hashHex = bytesToHex(hashBytes)
      setHash(hashHex)

      // Submit deed to Ceramic via ComposeDB
      const result = await composeClient.executeQuery(`
        mutation CreateDeed($input: CreateDeedInput!) {
          createDeed(input: $input) {
            document { id }
          }
        }
      `, {
        input: {
          content: {
            actionType: 'signal',
            proofHash: hashHex,
            description: signal,
            timestamp: new Date().toISOString(),
          },
        },
      })

      if (result.errors?.length) {
        console.warn('Deed mutation errors:', result.errors)
      } else {
        console.log('Deed created:', result.data)
        const deedIdentifier = (result.data as Record<string, any>)?.createDeed?.document?.id ?? hashHex
        broadcastDeedEvent(
          'signal',
          deedIdentifier,
          `New deed signal uploaded: ${signal} ${hashHex}`
        )
      }

      setSignal('')
    } catch (err) {
      console.error('Error submitting signal:', err)
      setError('Failed to submit signal. Check console for details.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="space-y-4">
        <p className="text-sm text-gray-600">
          You must connect a DID before submitting a signal.
        </p>
        <button
          onClick={loginWithKeypair}
          className="btn btn-primary w-full"
        >
          🔑 Connect DID first
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-600">
        Upload proof of work or expertise. A hash commitment will be created.
      </p>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          value={signal}
          onChange={(e) => setSignal(e.target.value)}
          placeholder="Describe your signal (expertise, project, contribution)..."
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-trust-500 focus:border-transparent"
          rows={4}
          required
        />
        
        <button
          type="submit"
          disabled={!signal || isSubmitting}
          className="btn btn-primary w-full disabled:opacity-50"
        >
          {isSubmitting ? 'Submitting...' : 'Submit Signal'}
        </button>
      </form>

      {error && (
        <div className="p-3 bg-red-50 rounded border border-red-200">
          <p className="text-xs text-red-700">{error}</p>
        </div>
      )}

      {hash && (
        <div className="p-3 bg-green-50 rounded border border-green-200">
          <p className="text-xs font-semibold text-green-800 mb-1">
            Signal Hash Created
          </p>
          <p className="text-xs font-mono text-green-700 break-all">
            {hash}
          </p>
        </div>
      )}
    </div>
  )
}
