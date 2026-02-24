'use client'

import { useState, useEffect } from 'react'
import { DID } from 'dids'
import { Ed25519Provider } from 'key-did-provider-ed25519'
import { getResolver } from 'key-did-resolver'

export function useDID() {
  const [did, setDid] = useState<string | null>(null)
  const [isConnecting, setIsConnecting] = useState(false)

  useEffect(() => {
    // Check if DID exists in localStorage
    const storedDID = localStorage.getItem('deed-ledger-did')
    if (storedDID) {
      setDid(storedDID)
    }
  }, [])

  const connect = async () => {
    setIsConnecting(true)
    try {
      // Generate a random seed (32 bytes)
      // In production, use proper key management or wallet connection
      const seed = new Uint8Array(32)
      crypto.getRandomValues(seed)

      // Create DID with Ed25519 provider
      const provider = new Ed25519Provider(seed)
      const didInstance = new DID({ provider, resolver: getResolver() })
      
      await didInstance.authenticate()

      // Store DID
      const didString = didInstance.id
      setDid(didString)
      localStorage.setItem('deed-ledger-did', didString)
      
      // In production, also store seed securely or use wallet
    } catch (error) {
      console.error('Error connecting DID:', error)
    } finally {
      setIsConnecting(false)
    }
  }

  const disconnect = () => {
    setDid(null)
    localStorage.removeItem('deed-ledger-did')
  }

  return { did, connect, disconnect, isConnecting }
}
