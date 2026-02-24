'use client';

import { useEffect, useState } from 'react';
import { useDIDAuth } from '../../context/DIDContext';
import { composeClient } from '../../lib/ceramic';
import { formatDistanceToNow } from 'date-fns';
import { broadcastDeedEvent } from '../lib/nostr';

type RecoveryStatus = 'pending' | 'approved' | 'rejected';

type ScarredDeed = {
  id: string;
  description: string;
  createdAt: string;
  recoveryStatus?: RecoveryStatus;
  recoveryId?: string;
};

export default function ScarRecovery() {
  const { isAuthenticated, did } = useDIDAuth();
  const [scarredDeeds, setScarredDeeds] = useState<ScarredDeed[]>([]);
  const [recoveryNotes, setRecoveryNotes] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const loadScarredDeeds = async () => {
    if (!did) return;

    const deedsResult = await composeClient.executeQuery(`
      query {
        deedIndex(filters: { and: [
          { controller: { equalTo: "${did.id}" } },
          { type: { equalTo: "dispute" } }
        ]}, first: 20) {
          edges {
            node {
              id
              description
              createdAt
            }
          }
        }
      }
    `);

    const deeds: ScarredDeed[] = (
      (deedsResult.data as Record<string, any>)?.deedIndex?.edges ?? []
    ).map((e: Record<string, any>) => e.node as ScarredDeed);

    const recoveryResult = await composeClient.executeQuery(`
      query {
        recoveryDeedIndex(filters: { controller: { equalTo: "${did.id}" } }, first: 50) {
          edges {
            node {
              id
              deedId
              status
            }
          }
        }
      }
    `);

    const recoveries: Array<{ id: string; deedId: string; status: RecoveryStatus }> = (
      (recoveryResult.data as Record<string, any>)?.recoveryDeedIndex?.edges ?? []
    ).map((e: Record<string, any>) => e.node);

    const recoveryByDeedId = Object.fromEntries(
      recoveries.map((r) => [r.deedId, { status: r.status, id: r.id }])
    );

    setScarredDeeds(
      deeds.map((deed) => ({
        ...deed,
        recoveryStatus: recoveryByDeedId[deed.id]?.status,
        recoveryId: recoveryByDeedId[deed.id]?.id,
      }))
    );
    setLoading(false);
  };

  useEffect(() => {
    if (isAuthenticated) loadScarredDeeds();
    // loadScarredDeeds is defined in render scope; including it would cause an infinite loop
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  const submitRecovery = async (deedId: string) => {
    const recoveryNote = recoveryNotes[deedId]?.trim();
    if (!recoveryNote || !did) return;
    setSubmitting(deedId);
    try {
      await composeClient.executeQuery(
        `mutation SubmitRecovery($deedId: ID!, $recoveryNote: String!, $recovererDID: String!) {
          submitRecovery(input: { deedId: $deedId, recoveryNote: $recoveryNote, recovererDID: $recovererDID }) {
            document { id }
          }
        }`,
        { deedId, recoveryNote, recovererDID: did.id }
      );
      await broadcastDeedEvent('recovery', deedId, `Recovery submitted: ${recoveryNote}`);
      alert('🩹 Recovery submitted — observers will review');
      await loadScarredDeeds();
    } finally {
      setSubmitting(null);
    }
  };

  if (!isAuthenticated) return <div className="text-red-500">Login first to submit recovery.</div>;
  if (loading) return <div>Loading scars...</div>;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-2 text-white">Scar Recovery</h1>
      <p className="text-zinc-400 mb-8 text-sm">
        Scars over bans — explain, rehabilitate, and let the record speak.
      </p>

      {scarredDeeds.length === 0 && (
        <p className="text-zinc-400">No active scars on your record. Keep it that way.</p>
      )}

      <div className="space-y-6">
        {scarredDeeds.map((deed) => (
          <div key={deed.id} className="bg-zinc-900 border border-red-900 p-6 rounded-xl">
            <div className="flex justify-between mb-3">
              <span className="text-red-400 font-bold text-sm uppercase tracking-widest">
                🩸 Scarred Deed
              </span>
              <span className="text-zinc-500 text-sm">
                {formatDistanceToNow(new Date(deed.createdAt), { addSuffix: true })}
              </span>
            </div>

            <p className="text-white mb-2">{deed.description}</p>

            {deed.recoveryStatus === 'pending' && (
              <div className="bg-amber-950 border border-amber-700 px-4 py-3 rounded-lg text-amber-300 text-sm">
                ⏳ Recovery pending — observers are reviewing
              </div>
            )}

            {deed.recoveryStatus === 'approved' && (
              <div className="bg-emerald-950 border border-emerald-700 px-4 py-3 rounded-lg text-emerald-300 text-sm">
                ✅ Recovery approved — scar weight reduced
              </div>
            )}

            {deed.recoveryStatus === 'rejected' && (
              <div className="space-y-3">
                <div className="bg-red-950 border border-red-800 px-4 py-3 rounded-lg text-red-300 text-sm">
                  ❌ Recovery rejected — address the root issue and try again
                </div>
                <textarea
                  className="w-full bg-zinc-800 border border-zinc-600 rounded-lg p-3 text-white text-sm resize-none focus:outline-none focus:border-amber-500"
                  rows={3}
                  placeholder="Explain what you've done differently to address the original concern..."
                  value={recoveryNotes[deed.id] ?? ''}
                  onChange={(e) =>
                    setRecoveryNotes((prev) => ({ ...prev, [deed.id]: e.target.value }))
                  }
                />
                <button
                  onClick={() => submitRecovery(deed.id)}
                  disabled={submitting === deed.id || !recoveryNotes[deed.id]?.trim()}
                  className="w-full bg-amber-600 hover:bg-amber-500 disabled:opacity-50 disabled:cursor-not-allowed py-3 rounded-xl font-bold transition"
                >
                  {submitting === deed.id ? 'Submitting...' : '🩹 Re-submit Recovery'}
                </button>
              </div>
            )}

            {!deed.recoveryStatus && (
              <div className="mt-4 space-y-2">
                <textarea
                  className="w-full bg-zinc-800 border border-zinc-600 rounded-lg p-3 text-white text-sm resize-none focus:outline-none focus:border-amber-500"
                  rows={3}
                  placeholder="Explain what happened and what you've done to address it..."
                  value={recoveryNotes[deed.id] ?? ''}
                  onChange={(e) =>
                    setRecoveryNotes((prev) => ({ ...prev, [deed.id]: e.target.value }))
                  }
                />
                <button
                  onClick={() => submitRecovery(deed.id)}
                  disabled={submitting === deed.id || !recoveryNotes[deed.id]?.trim()}
                  className="w-full bg-amber-600 hover:bg-amber-500 disabled:opacity-50 disabled:cursor-not-allowed py-3 rounded-xl font-bold transition"
                >
                  {submitting === deed.id ? 'Submitting...' : '🩹 Submit Recovery'}
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
