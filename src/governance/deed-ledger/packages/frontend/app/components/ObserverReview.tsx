'use client';

import { useEffect, useState } from 'react';
import { useDIDAuth } from '../../context/DIDContext';
import { composeClient } from '../../lib/ceramic';
import { formatDistanceToNow } from 'date-fns';
import { broadcastDeedEvent } from '../lib/nostr';

type PendingDeed = {
  id: string;
  ownerDID: string;
  actionType: string;
  description: string;
  proofHash: string;
  timestamp: string;
  verifiers: string[];
};

type PendingRecovery = {
  id: string;
  deedId: string;
  recoveryNote: string;
  recovererDID: string;
  createdAt: string;
};

export default function ObserverReview() {
  const { isAuthenticated, did } = useDIDAuth();
  const [pendingDeeds, setPendingDeeds] = useState<PendingDeed[]>([]);
  const [pendingRecoveries, setPendingRecoveries] = useState<PendingRecovery[]>([]);
  const [loading, setLoading] = useState(true);

  const loadPending = async () => {
    if (!did) return;
    const result = await composeClient.executeQuery(`
      query {
        deedIndex(filters: { status: { equalTo: "pending" } }, first: 20) {
          edges {
            node {
              id
              ownerDID
              actionType
              description
              proofHash
              timestamp
              verifiers
            }
          }
        }
      }
    `);
    setPendingDeeds(((result.data as Record<string, any>)?.deedIndex?.edges ?? []).map((e: Record<string, any>) => e.node as PendingDeed));
    setLoading(false);
  };

  const loadPendingRecoveries = async () => {
    if (!did) return;
    const result = await composeClient.executeQuery(`
      query {
        recoveryDeedIndex(filters: { status: { equalTo: "pending" } }, first: 20) {
          edges {
            node {
              id
              deedId
              recoveryNote
              recovererDID
              createdAt
            }
          }
        }
      }
    `);
    setPendingRecoveries(
      ((result.data as Record<string, any>)?.recoveryDeedIndex?.edges ?? []).map(
        (e: Record<string, any>) => e.node as PendingRecovery
      )
    );
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadPending();
      loadPendingRecoveries();
    }
    // loadPending/loadPendingRecoveries are defined in render scope; including them would cause an infinite loop
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  const verifyDeed = async (deedId: string, approve: boolean, scarNote?: string) => {
    if (approve) {
      await composeClient.executeQuery(
        `mutation VerifyDeed($id: ID!, $verifierDID: String!) {
          verifyDeed(input: { id: $id, verifierDID: $verifierDID }) { document { id } }
        }`,
        { id: deedId, verifierDID: did!.id }
      );
      broadcastDeedEvent('verify', deedId, 'Deed verified +influence by observer');
    } else {
      await composeClient.executeQuery(
        `mutation AddScar($deedId: ID!, $scarNote: String!, $scarverDID: String!) {
          addScar(input: { deedId: $deedId, scarNote: $scarNote, scarverDID: $scarverDID }) { document { id } }
        }`,
        { deedId, scarNote: scarNote ?? 'Disputed', scarverDID: did!.id }
      );
      broadcastDeedEvent('scar', deedId, `Scar added: ${scarNote ?? 'Disputed'}`);
    }
    alert(approve ? '✅ Verified — influence awarded' : '🩸 Scar added — visible mark');
    loadPending();
  };

  const reviewRecovery = async (recoveryId: string, deedId: string, approve: boolean) => {
    await composeClient.executeQuery(
      `mutation ReviewRecovery($id: ID!, $status: String!, $reviewerDID: String!) {
        reviewRecovery(input: { id: $id, status: $status, reviewerDID: $reviewerDID }) {
          document { id }
        }
      }`,
      { id: recoveryId, status: approve ? 'approved' : 'rejected', reviewerDID: did!.id }
    );
    if (approve) {
      broadcastDeedEvent('recovery_approved', deedId, 'Recovery approved +rehab');
    } else {
      broadcastDeedEvent('recovery_rejected', deedId, 'Recovery rejected');
    }
    alert(approve ? '✅ Recovery approved — scar weight reduced' : '❌ Recovery rejected');
    loadPendingRecoveries();
  };

  if (!isAuthenticated) return <div className="text-red-500">Login first, Observer.</div>;
  if (loading) return <div>Scanning deeds...</div>;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8 text-white">Observer Review — Verify or Scar</h1>

      {pendingDeeds.length === 0 && <p className="text-zinc-400">No pending deeds. Go make some or chill.</p>}

      <div className="space-y-6">
        {pendingDeeds.map((deed) => (
          <div key={deed.id} className="bg-zinc-900 border border-zinc-700 p-6 rounded-xl">
            <div className="flex justify-between mb-4">
              <div>
                <span className="text-emerald-400 font-mono text-sm">{deed.ownerDID.slice(0, 12)}...</span>
                <span className="ml-3 text-amber-400 uppercase text-xs tracking-widest">{deed.actionType}</span>
              </div>
              <span className="text-zinc-500 text-sm">
                {formatDistanceToNow(new Date(deed.timestamp), { addSuffix: true })}
              </span>
            </div>

            <p className="text-lg text-white mb-4">{deed.description}</p>
            <p className="font-mono text-xs text-zinc-500 break-all mb-6">Proof: {deed.proofHash}</p>

            <div className="flex gap-3">
              <button
                onClick={() => verifyDeed(deed.id, true)}
                className="flex-1 bg-emerald-600 hover:bg-emerald-500 py-4 rounded-xl font-bold text-lg transition"
              >
                ✅ VERIFY — +Influence
              </button>
              <button
                onClick={() => {
                  const note = prompt('Scar note (be honest, be brutal):');
                  if (note) verifyDeed(deed.id, false, note);
                }}
                className="flex-1 bg-red-600 hover:bg-red-500 py-4 rounded-xl font-bold text-lg transition"
              >
                🩸 ADD SCAR
              </button>
            </div>
          </div>
        ))}
      </div>

      {pendingRecoveries.length > 0 && (
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-6 text-amber-400">Review Recovery — Pending Rehab</h2>
          <div className="space-y-6">
            {pendingRecoveries.map((recovery) => (
              <div key={recovery.id} className="bg-zinc-900 border border-amber-900 p-6 rounded-xl">
                <div className="flex justify-between mb-3">
                  <span className="text-amber-400 font-mono text-sm">
                    {recovery.recovererDID.slice(0, 12)}...
                  </span>
                  <span className="text-zinc-500 text-sm">
                    {formatDistanceToNow(new Date(recovery.createdAt), { addSuffix: true })}
                  </span>
                </div>
                <p className="text-zinc-400 text-xs mb-2">
                  Deed: <span className="font-mono">{recovery.deedId}</span>
                </p>
                <p className="text-white mb-6">{recovery.recoveryNote}</p>
                <div className="flex gap-3">
                  <button
                    onClick={() => reviewRecovery(recovery.id, recovery.deedId, true)}
                    className="flex-1 bg-emerald-600 hover:bg-emerald-500 py-3 rounded-xl font-bold transition"
                  >
                    ✅ APPROVE — Reduce Scar
                  </button>
                  <button
                    onClick={() => reviewRecovery(recovery.id, recovery.deedId, false)}
                    className="flex-1 bg-red-600 hover:bg-red-500 py-3 rounded-xl font-bold transition"
                  >
                    ❌ REJECT
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
