'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { DIDSession } from 'did-session';
import { Ed25519Provider } from 'key-did-provider-ed25519';
import { getResolver } from 'key-did-resolver';
import { DID } from 'dids';
import { EthereumWebAuth, getAccountId } from '@didtools/pkh-ethereum';
import { useConnections, useConnect, useDisconnect } from 'wagmi';
import { injected } from 'wagmi/connectors';
import { composeClient } from '../lib/ceramic';

type DIDAuthContextType = {
  did: DID | null;
  session: DIDSession | null;
  isAuthenticated: boolean;
  loading: boolean;
  loginWithKeypair: () => Promise<void>;
  loginWithWallet: () => Promise<void>;
  logout: () => void;
  address?: string;
};

const DIDAuthContext = createContext<DIDAuthContextType | undefined>(undefined);

const SEED_KEY = 'deedLedgerSeed';
const SESSION_KEY = 'deedLedgerSession';

/** Convert a hex string to a Uint8Array without requiring a Buffer polyfill. */
function hexToBytes(hex: string): Uint8Array {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < bytes.length; i++) {
    bytes[i] = parseInt(hex.slice(i * 2, i * 2 + 2), 16);
  }
  return bytes;
}

/** Convert a Uint8Array to a hex string without requiring a Buffer polyfill. */
function bytesToHex(bytes: Uint8Array): string {
  return Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

export function DIDAuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<DIDSession | null>(null);
  const [did, setDID] = useState<DID | null>(null);
  const [loading, setLoading] = useState(true);
  const [address, setAddress] = useState<string | undefined>();

  const connections = useConnections();
  const { connect } = useConnect();
  const { disconnect } = useDisconnect();

  // Auto-restore session from localStorage on mount
  useEffect(() => {
    const restoreSession = async () => {
      try {
        const storedSeed = localStorage.getItem(SEED_KEY);
        const storedSession = localStorage.getItem(SESSION_KEY);

        if (storedSeed) {
          // Restore did:key from persisted seed
          const seed = hexToBytes(storedSeed);
          const provider = new Ed25519Provider(seed);
          const restoredDid = new DID({ provider, resolver: getResolver() });
          await restoredDid.authenticate();
          setDID(restoredDid);
          composeClient.setDID(restoredDid);
        } else if (storedSession) {
          // Restore did:pkh wallet session
          const restored = await DIDSession.fromSession(storedSession);
          if (!restored.isExpired && restored.hasSession) {
            setSession(restored);
            setDID(restored.did);
            composeClient.setDID(restored.did);
            const parent = restored.did.parent;
            if (parent?.includes('did:pkh')) {
              const parts = parent.split(':');
              setAddress(parts[parts.length - 1]);
            }
          } else {
            localStorage.removeItem(SESSION_KEY);
          }
        }
      } catch (e) {
        console.warn('Failed to restore DID session, clearing storage:', e);
        localStorage.removeItem(SEED_KEY);
        localStorage.removeItem(SESSION_KEY);
      } finally {
        setLoading(false);
      }
    };
    restoreSession();
  }, []);

  const loginWithKeypair = async () => {
    setLoading(true);
    try {
      const seed = new Uint8Array(32);
      crypto.getRandomValues(seed);

      const provider = new Ed25519Provider(seed);
      const newDid = new DID({ provider, resolver: getResolver() });
      await newDid.authenticate();

      setDID(newDid);
      composeClient.setDID(newDid);
      localStorage.removeItem(SESSION_KEY);
      localStorage.setItem(SEED_KEY, bytesToHex(seed));
    } finally {
      setLoading(false);
    }
  };

  const loginWithWallet = async () => {
    setLoading(true);
    try {
      // Request accounts via EIP-1193 provider
      const eth = (window as Window & { ethereum?: { request: (args: { method: string }) => Promise<string[]> } }).ethereum;
      if (!eth) throw new Error('No Ethereum provider found. Install MetaMask or similar wallet.');

      const addresses = await eth.request({ method: 'eth_requestAccounts' });
      const walletAddress = addresses[0];

      const accountId = await getAccountId(eth as Parameters<typeof getAccountId>[0], walletAddress);
      const authMethod = await EthereumWebAuth.getAuthMethod(
        eth as Parameters<typeof EthereumWebAuth.getAuthMethod>[0],
        accountId
      );

      // Cast to bypass peer-dep version mismatch between @didtools/cacao@2 (did-session) and @didtools/cacao@3 (@didtools/pkh-ethereum)
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const newSession = await DIDSession.authorize(authMethod as any, {
        resources: ['ceramic://*'],
      });

      setSession(newSession);
      setDID(newSession.did);
      setAddress(walletAddress);
      composeClient.setDID(newSession.did);
      localStorage.removeItem(SEED_KEY);
      localStorage.setItem(SESSION_KEY, newSession.serialize());

      // Also connect wagmi for UI state
      connect({ connector: injected() });
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem(SEED_KEY);
    localStorage.removeItem(SESSION_KEY);
    setSession(null);
    setDID(null);
    setAddress(undefined);
    // Note: CeramicClient does not expose a way to unset the DID; the stale DID
    // is safe to leave because isAuthenticated guards all mutation paths in the UI.
    // Disconnect any wagmi connections
    connections.forEach((c) => disconnect({ connector: c.connector }));
  };

  return (
    <DIDAuthContext.Provider
      value={{
        did,
        session,
        isAuthenticated: !!did,
        loading,
        loginWithKeypair,
        loginWithWallet,
        logout,
        address,
      }}
    >
      {children}
    </DIDAuthContext.Provider>
  );
}

export const useDIDAuth = () => {
  const ctx = useContext(DIDAuthContext);
  if (!ctx) throw new Error('useDIDAuth must be inside DIDAuthProvider');
  return ctx;
};
