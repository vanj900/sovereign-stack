// TypeScript types for the Ceramic reputation schema

export interface Signature {
  signer: string; // DID
  timestamp: string; // DateTime
  verification?: string;
}

export interface Deed {
  id: string;
  controller: string; // DID
  createdAt: string; // DateTime
  type: 'deed_completed' | 'vouch' | 'dispute' | string;
  description?: string;
  counterparty?: string; // DID
  signatures?: Signature[];
  linkedEventId?: string; // StreamID
  nicheTags?: string[];
}

export interface Scar {
  deedId: string; // StreamID
  scarNote: string;
  scarverDID: string; // DID
  createdAt: string; // DateTime
}

export type RecoveryStatus = 'pending' | 'approved' | 'rejected';

export interface RecoveryDeed {
  id: string;
  deedId: string; // StreamID — linked to the scarred Deed
  controller: string; // DID
  createdAt: string; // DateTime
  recoveryNote: string;
  recovererDID: string; // DID
  status: RecoveryStatus;
  reviewedAt?: string; // DateTime
  reviewerDID?: string; // DID
}

export interface NicheTag {
  tag: string;
  score: number;
  deedIds?: string[]; // StreamID[]
}

export type UserStatus = 'invite_pending' | 'signal_sent' | 'observer' | 'node';

export interface UserReputation {
  controller: string; // DID
  deedCount: number;
  totalScore: number;
  nicheTags?: NicheTag[];
  observers?: string[]; // DID[]
  status?: UserStatus;
  joinedAt: string; // DateTime
}
