// TypeScript types for the Ceramic reputation schema
// Includes the fractal organisational hierarchy: Node → Cell → Unit → Federation/Alliance

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

// ---------------------------------------------------------------------------
// Fractal Organisational Hierarchy: Node → Cell → Unit → Federation/Alliance
// ---------------------------------------------------------------------------

// The three kinds of sovereign agent a Node may represent.
export type NodeType = 'human' | 'sov_hab' | 'ghost_brain';

// A Context DID (cDID) is derived from a node's Master DID so the node can
// participate in a specific Cell without creating a universal activity trail.
export interface ContextDID {
  cDID: string;      // Context-specific derived DID
  masterDID: string; // Master DID it was derived from
  cellId: string;    // Cell this cDID is scoped to
  createdAt: string; // DateTime
}

// A Node is the basic unit of agency — one node, one vote.
// It holds a Master DID and derives Context DIDs per Cell.
// It belongs to exactly one Primary Home Cell and up to three Functional Cells.
export interface SovereignNode {
  id: string;
  masterDID: string;           // Master identity anchor
  contextDIDs?: ContextDID[];  // Per-cell derived DIDs
  type: NodeType;
  primaryHomeCellId?: string;  // Exactly one PHC
  functionalCellIds?: string[]; // Up to three concurrent FCs
  createdAt: string;           // DateTime
}

// Cells are either Primary Home Cells (one per node) or Functional Cells.
export type CellType = 'primary_home_cell' | 'functional_cell';

// A Cell is the core unit of social and technical coordination.
// Size is hard-capped at 3–7 nodes; exceeding seven triggers a horizontal fork.
export interface Cell {
  id: string;
  type: CellType;
  nodeIds: string[];     // 3–7 node IDs (anti-corruption hard cap)
  treasury?: number;     // Pooled resources managed by the Cell
  createdAt: string;     // DateTime
  forkedFromId?: string; // Present when this Cell was created by a fork
}

// A Bridge Contract is an auditable agreement between Cells inside a Unit,
// defining shared work, resource flows, and data exchange.
export type BridgeContractStatus = 'active' | 'completed' | 'expired';

export interface BridgeContract {
  id: string;
  cellIds: string[];              // Cells party to this contract
  description: string;
  terms: string;                  // Auditable terms of the agreement
  status: BridgeContractStatus;
  createdAt: string;              // DateTime
  expiresAt?: string;             // DateTime — optional expiry
}

// A Unit is a federation of 3–7 Cells (approximately 9–49 nodes).
// Once a Unit exceeds seven Cells it must fork horizontally.
export interface Unit {
  id: string;
  cellIds: string[];              // 3–7 cell IDs
  bridgeContractIds?: string[];   // Active Bridge Contract IDs
  createdAt: string;              // DateTime
  forkedFromId?: string;          // Present when created by a fork
}

// Federations and Alliances link Units for larger coordination.
// They are always opt-in, time-boxed, and carry a mandatory expiry so they
// can never harden into a permanent, centralised authority.
export type FederationAllianceType = 'federation' | 'alliance';

export interface FederationAlliance {
  id: string;
  type: FederationAllianceType;
  unitIds: string[];   // Participating Units (opt-in only)
  purpose: string;
  isOptIn: true;       // Structural invariant — never involuntary
  createdAt: string;   // DateTime
  expiresAt: string;   // DateTime — mandatory expiry
}
