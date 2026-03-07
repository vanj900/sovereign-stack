"""
Cell / Unit / Federation Hierarchy
====================================
Demonstrates the full fractal organisational hierarchy of the Sovereign Stack:

  Node → Cell → Unit → Federation / Alliance

Key rules enforced:

  * **Nodes**: one node, one vote; identified by a Master DID from which
    Context DIDs (cDIDs) are derived so each Cell only sees an opaque
    pseudonym, not a universal identity trail.

  * **Cells**: 3–7 nodes (anti-corruption hard cap). A node belongs to
    exactly one Primary Home Cell (PHC) and up to three Functional Cells
    (FCs). When membership exceeds seven the Cell forks horizontally.

  * **Units**: 3–7 Cells (~9–49 nodes). Inter-cell work is coordinated
    via Bridge Contracts. When membership exceeds seven the Unit forks.

  * **Federations / Alliances**: opt-in, time-boxed, always expiring — they
    never harden into permanent, centralised authority.

This script is self-contained — no imports from other example files needed.

Run:
    python 07_cell_unit_hierarchy.py

Expected output includes:
    === Cell / Unit / Federation Hierarchy ===
    [node] alice    created  DID=did:sov:alice
    ...
    [cell] PHC-1    formed   (3 nodes)
    ...
    [fork] PHC-1 → fork into Cell-fork-0, Cell-fork-1 (8 nodes exceeded limit)
    ...
    [unit] Unit-1   formed   (3 cells)
    [bridge] BC-1   created  between PHC-1 and FC-energy
    [federation] FED-1  formed  expires=...
"""

import hashlib
import json
import time
import uuid


# ===========================================================================
# Node — the basic unit of agency
# ===========================================================================

class SovereignNode:
    """
    A sovereign agent: human, SOV-HAB household, or GhostBrain AI.

    Holds a Master DID and derives per-Cell Context DIDs (cDIDs) to
    participate in different cells without creating a cross-cell identity
    trail.
    """

    NODE_TYPES = ("human", "sov_hab", "ghost_brain")

    def __init__(self, name: str, node_type: str = "human"):
        if node_type not in self.NODE_TYPES:
            raise ValueError(f"Unknown node type: {node_type!r}")
        self.name = name
        self.node_type = node_type
        self.master_did: str = f"did:sov:{name}"
        self._context_dids: dict = {}   # cell_id → cDID
        self._phc_id: str | None = None
        self._fc_ids: list = []         # max three
        print(f"[node] {name:<8} created  DID={self.master_did}  type={node_type}")

    # ------------------------------------------------------------------
    # Context DID derivation
    # ------------------------------------------------------------------

    def derive_context_did(self, cell_id: str) -> str:
        """
        Derive a context-specific DID for *cell_id*.

        The cDID is a deterministic hash of the master DID and the cell ID so
        that different cells see different pseudonyms for the same node.
        """
        if cell_id not in self._context_dids:
            seed = f"{self.master_did}:{cell_id}"
            digest = hashlib.sha256(seed.encode()).hexdigest()[:16]
            self._context_dids[cell_id] = f"did:cid:{digest}"
        return self._context_dids[cell_id]

    # ------------------------------------------------------------------
    # Cell membership helpers
    # ------------------------------------------------------------------

    def set_phc(self, cell_id: str) -> None:
        """Assign the node's Primary Home Cell (exactly one allowed)."""
        if self._phc_id is not None:
            raise ValueError(
                f"{self.name} already belongs to PHC {self._phc_id!r}; "
                "a node may only have one PHC"
            )
        self._phc_id = cell_id

    def join_fc(self, cell_id: str) -> None:
        """Add a Functional Cell (maximum three concurrent FCs)."""
        if cell_id in self._fc_ids:
            return
        if len(self._fc_ids) >= 3:
            raise ValueError(
                f"{self.name} already belongs to three Functional Cells; "
                "join limit reached"
            )
        self._fc_ids.append(cell_id)

    @property
    def phc_id(self) -> str | None:
        return self._phc_id

    @property
    def fc_ids(self) -> list:
        return list(self._fc_ids)


# ===========================================================================
# Cell — 3 to 7 nodes
# ===========================================================================

CELL_MIN = 3
CELL_MAX = 7


class Cell:
    """
    Core unit of social and technical coordination.

    Size is hard-capped at 3–7 nodes. Exceeding seven triggers a horizontal
    fork. Cells maintain their own treasury and make decisions democratically
    via signed receipts.
    """

    CELL_TYPES = ("primary_home_cell", "functional_cell")

    def __init__(self, cell_id: str, cell_type: str = "primary_home_cell",
                 forked_from: str | None = None):
        if cell_type not in self.CELL_TYPES:
            raise ValueError(f"Unknown cell type: {cell_type!r}")
        self.cell_id = cell_id
        self.cell_type = cell_type
        self.forked_from = forked_from
        self._nodes: list = []    # SovereignNode instances
        self.treasury: int = 0
        print(
            f"[cell] {cell_id:<12} created  type={cell_type}"
            + (f"  forked_from={forked_from}" if forked_from else "")
        )

    # ------------------------------------------------------------------
    # Membership
    # ------------------------------------------------------------------

    def add_node(self, node: SovereignNode) -> None:
        """
        Add a node to this cell.

        Raises ``ValueError`` if adding the node would break the 7-node cap,
        or if the node already belongs to this cell.
        """
        if any(n.name == node.name for n in self._nodes):
            raise ValueError(f"{node.name} is already a member of {self.cell_id}")
        if len(self._nodes) >= CELL_MAX:
            raise ValueError(
                f"{self.cell_id} has reached the maximum of {CELL_MAX} nodes; "
                "fork before adding more members"
            )
        self._nodes.append(node)
        # Assign Cell membership on the node
        if self.cell_type == "primary_home_cell":
            node.set_phc(self.cell_id)
        else:
            node.join_fc(self.cell_id)
        # Each node derives a cDID for this cell
        cdid = node.derive_context_did(self.cell_id)
        print(
            f"[cell] {node.name:<8} joined  {self.cell_id}  "
            f"cDID={cdid}  members={len(self._nodes)}"
        )

    def remove_node(self, node_name: str) -> SovereignNode:
        """Remove a node by name and return it."""
        for i, n in enumerate(self._nodes):
            if n.name == node_name:
                self._nodes.pop(i)
                print(
                    f"[cell] {node_name:<8} left    {self.cell_id}  "
                    f"members={len(self._nodes)}"
                )
                return n
        raise ValueError(f"{node_name!r} is not a member of {self.cell_id}")

    @property
    def size(self) -> int:
        return len(self._nodes)

    @property
    def nodes(self) -> list:
        return list(self._nodes)

    def is_quorate(self) -> bool:
        """A Cell needs at least CELL_MIN members to operate."""
        return len(self._nodes) >= CELL_MIN

    # ------------------------------------------------------------------
    # Treasury
    # ------------------------------------------------------------------

    def contribute(self, amount: int, contributor: str = "anonymous") -> None:
        self.treasury += amount
        print(
            f"[treasury] {contributor:<8} contributed {amount}  "
            f"{self.cell_id} treasury={self.treasury}"
        )

    # ------------------------------------------------------------------
    # Governance (simple majority, one node one vote)
    # ------------------------------------------------------------------

    def vote(self, proposal: str, votes: dict) -> str:
        """
        Tally a dict of ``{node_name: 'APPROVE'|'REJECT'}`` using a simple
        majority.  Returns ``'PASSED'`` or ``'FAILED'``.
        """
        if not self.is_quorate():
            raise ValueError(f"{self.cell_id} is not quorate (needs ≥{CELL_MIN} nodes)")
        members = {n.name for n in self._nodes}
        for voter in votes:
            if voter not in members:
                raise ValueError(f"{voter!r} is not a member of {self.cell_id}")
        approve = sum(1 for v in votes.values() if v == "APPROVE")
        reject  = sum(1 for v in votes.values() if v == "REJECT")
        result = "PASSED" if approve > reject else "FAILED"
        print(
            f"[vote] {self.cell_id}  proposal={proposal!r}  "
            f"approve={approve}  reject={reject}  → {result}"
        )
        return result

    # ------------------------------------------------------------------
    # Fork
    # ------------------------------------------------------------------

    def fork(self) -> tuple:
        """
        Horizontally fork this Cell into two new Cells when the node count
        exceeds CELL_MAX.

        Splits nodes roughly evenly. Returns a tuple of two new Cell instances.
        """
        if self.size <= CELL_MAX:
            raise ValueError(
                f"Cannot fork {self.cell_id}: only {self.size} nodes "
                f"(fork required when > {CELL_MAX})"
            )
        mid = self.size // 2
        left_nodes  = self._nodes[:mid]
        right_nodes = self._nodes[mid:]
        left_id  = f"{self.cell_id}-fork-0"
        right_id = f"{self.cell_id}-fork-1"
        print(
            f"[fork] {self.cell_id} → fork into {left_id}, {right_id} "
            f"({self.size} nodes exceeded limit)"
        )
        left  = Cell(left_id,  self.cell_type, forked_from=self.cell_id)
        right = Cell(right_id, self.cell_type, forked_from=self.cell_id)
        # Re-add nodes; this re-derives cDIDs and re-registers PHC/FC on each node
        for node in left_nodes:
            # Reset the node's cell membership so add_node bookkeeping works
            _reset_node_membership(node, self.cell_id, left_id, self.cell_type)
            left._nodes.append(node)
            cdid = node.derive_context_did(left_id)
            print(
                f"[cell] {node.name:<8} joined  {left_id}  "
                f"cDID={cdid}  members={len(left._nodes)}"
            )
        for node in right_nodes:
            _reset_node_membership(node, self.cell_id, right_id, self.cell_type)
            right._nodes.append(node)
            cdid = node.derive_context_did(right_id)
            print(
                f"[cell] {node.name:<8} joined  {right_id}  "
                f"cDID={cdid}  members={len(right._nodes)}"
            )
        return left, right


def _reset_node_membership(
    node: SovereignNode, old_cell_id: str, new_cell_id: str, cell_type: str
) -> None:
    """Update node's internal cell membership pointers after a fork."""
    if cell_type == "primary_home_cell":
        if node._phc_id == old_cell_id:
            node._phc_id = new_cell_id
    else:
        if old_cell_id in node._fc_ids:
            idx = node._fc_ids.index(old_cell_id)
            node._fc_ids[idx] = new_cell_id


# ===========================================================================
# Bridge Contract — inter-cell coordination within a Unit
# ===========================================================================

class BridgeContract:
    """
    Auditable agreement between two or more Cells inside a Unit.

    Defines shared work, resource flows, and data exchange.
    """

    STATUSES = ("active", "completed", "expired")

    def __init__(self, contract_id: str, cell_ids: list, description: str,
                 terms: str, duration_seconds: int = 86400):
        if len(cell_ids) < 2:
            raise ValueError("A BridgeContract requires at least two cells")
        self.contract_id = contract_id
        self.cell_ids = list(cell_ids)
        self.description = description
        self.terms = terms
        self.status = "active"
        self.created_at = int(time.time())
        self.expires_at = self.created_at + duration_seconds
        print(
            f"[bridge] {contract_id:<8} created  "
            f"between {' & '.join(cell_ids)}  "
            f"expires_in={duration_seconds}s"
        )

    def is_expired(self) -> bool:
        return int(time.time()) >= self.expires_at

    def expire(self) -> None:
        self.status = "expired"
        print(f"[bridge] {self.contract_id:<8} expired")

    def complete(self) -> None:
        self.status = "completed"
        print(f"[bridge] {self.contract_id:<8} completed")


# ===========================================================================
# Unit — 3 to 7 Cells
# ===========================================================================

UNIT_MIN = 3
UNIT_MAX = 7


class Unit:
    """
    A federation of 3–7 Cells (~9–49 nodes).

    Once the Unit exceeds seven Cells it must fork horizontally, mirroring
    the same rule that governs individual Cells.
    """

    def __init__(self, unit_id: str, forked_from: str | None = None):
        self.unit_id = unit_id
        self.forked_from = forked_from
        self._cells: list = []          # Cell instances
        self._bridge_contracts: list = []
        print(
            f"[unit] {unit_id:<10} created"
            + (f"  forked_from={forked_from}" if forked_from else "")
        )

    # ------------------------------------------------------------------
    # Cell membership
    # ------------------------------------------------------------------

    def add_cell(self, cell: Cell) -> None:
        if any(c.cell_id == cell.cell_id for c in self._cells):
            raise ValueError(f"{cell.cell_id} is already a member of {self.unit_id}")
        if len(self._cells) >= UNIT_MAX:
            raise ValueError(
                f"{self.unit_id} has reached the maximum of {UNIT_MAX} cells; "
                "fork before adding more"
            )
        self._cells.append(cell)
        print(
            f"[unit] {cell.cell_id:<12} added to {self.unit_id}  "
            f"cells={len(self._cells)}"
        )

    @property
    def size(self) -> int:
        return len(self._cells)

    @property
    def cells(self) -> list:
        return list(self._cells)

    def is_quorate(self) -> bool:
        return len(self._cells) >= UNIT_MIN

    def node_count(self) -> int:
        return sum(c.size for c in self._cells)

    # ------------------------------------------------------------------
    # Bridge Contracts
    # ------------------------------------------------------------------

    def add_bridge_contract(self, contract: BridgeContract) -> None:
        for cid in contract.cell_ids:
            if not any(c.cell_id == cid for c in self._cells):
                raise ValueError(
                    f"Cell {cid!r} is not part of {self.unit_id}; "
                    "bridge contracts must be between member cells"
                )
        self._bridge_contracts.append(contract)
        print(
            f"[unit] {self.unit_id}  bridge contract {contract.contract_id} registered"
        )

    @property
    def bridge_contracts(self) -> list:
        return list(self._bridge_contracts)

    # ------------------------------------------------------------------
    # Fork
    # ------------------------------------------------------------------

    def fork(self) -> tuple:
        """
        Horizontally fork this Unit into two new Units when the cell count
        exceeds UNIT_MAX.

        Returns a tuple of two new Unit instances.
        """
        if self.size <= UNIT_MAX:
            raise ValueError(
                f"Cannot fork {self.unit_id}: only {self.size} cells "
                f"(fork required when > {UNIT_MAX})"
            )
        mid = self.size // 2
        left_cells  = self._cells[:mid]
        right_cells = self._cells[mid:]
        left_id  = f"{self.unit_id}-fork-0"
        right_id = f"{self.unit_id}-fork-1"
        print(
            f"[fork] {self.unit_id} → fork into {left_id}, {right_id} "
            f"({self.size} cells exceeded limit)"
        )
        left  = Unit(left_id,  forked_from=self.unit_id)
        right = Unit(right_id, forked_from=self.unit_id)
        for c in left_cells:
            left._cells.append(c)
            print(f"[unit] {c.cell_id:<12} moved to {left_id}")
        for c in right_cells:
            right._cells.append(c)
            print(f"[unit] {c.cell_id:<12} moved to {right_id}")
        return left, right


# ===========================================================================
# FederationAlliance — opt-in, time-boxed, always expiring
# ===========================================================================

class FederationAlliance:
    """
    Opt-in, time-boxed coordination layer above the Unit level.

    Covers Federations (tight resource sharing) and Alliances (looser,
    mission-specific coordination such as Crisis Mesh activations).  Both
    carry a mandatory expiry so they can never harden into permanent,
    centralised authority.
    """

    TYPES = ("federation", "alliance")

    def __init__(self, fa_id: str, fa_type: str, units: list,
                 purpose: str, duration_seconds: int = 2592000):
        if fa_type not in self.TYPES:
            raise ValueError(f"Unknown type: {fa_type!r}")
        if len(units) < 1:
            raise ValueError("A FederationAlliance requires at least one unit")
        self.fa_id = fa_id
        self.fa_type = fa_type
        self._units: list = list(units)
        self.purpose = purpose
        self.created_at = int(time.time())
        self.expires_at = self.created_at + duration_seconds
        print(
            f"[{fa_type}] {fa_id:<8} formed  "
            f"units={[u.unit_id for u in units]}  "
            f"purpose={purpose!r}  "
            f"expires_in={duration_seconds}s"
        )

    def add_unit(self, unit: Unit) -> None:
        """Opt-in participation — units join voluntarily."""
        if any(u.unit_id == unit.unit_id for u in self._units):
            return
        self._units.append(unit)
        print(
            f"[{self.fa_type}] {unit.unit_id} opted into {self.fa_id}  "
            f"total_units={len(self._units)}"
        )

    @property
    def is_opt_in(self) -> bool:
        """Structural invariant — participation is always voluntary."""
        return True

    def is_expired(self) -> bool:
        return int(time.time()) >= self.expires_at

    @property
    def units(self) -> list:
        return list(self._units)


# ===========================================================================
# Main demo
# ===========================================================================

def main() -> None:
    print("=== Cell / Unit / Federation Hierarchy ===\n")

    # -----------------------------------------------------------------------
    # Phase 1: Create nodes of different types
    # -----------------------------------------------------------------------
    print("--- Phase 1: Node creation ---")
    alice   = SovereignNode("alice",   "human")
    bob     = SovereignNode("bob",     "human")
    carol   = SovereignNode("carol",   "human")
    dave    = SovereignNode("dave",    "human")
    eve     = SovereignNode("eve",     "sov_hab")
    frank   = SovereignNode("frank",   "human")
    grace   = SovereignNode("grace",   "human")
    hal     = SovereignNode("hal",     "ghost_brain")
    # Extra nodes used to trigger a cell fork
    ivan    = SovereignNode("ivan",    "human")
    print()

    # -----------------------------------------------------------------------
    # Phase 2: Form a Primary Home Cell (PHC-1) — alice, bob, carol
    # -----------------------------------------------------------------------
    print("--- Phase 2: Primary Home Cell ---")
    phc1 = Cell("PHC-1", "primary_home_cell")
    phc1.add_node(alice)
    phc1.add_node(bob)
    phc1.add_node(carol)
    print(f"[cell] PHC-1 formed  ({phc1.size} nodes)  quorate={phc1.is_quorate()}")
    print()

    # -----------------------------------------------------------------------
    # Phase 3: Form a Functional Cell (FC-energy) — dave, eve, frank
    # -----------------------------------------------------------------------
    print("--- Phase 3: Functional Cell ---")
    fc_energy = Cell("FC-energy", "functional_cell")
    fc_energy.add_node(dave)
    fc_energy.add_node(eve)
    fc_energy.add_node(frank)
    print(f"[cell] FC-energy formed  ({fc_energy.size} nodes)  quorate={fc_energy.is_quorate()}")
    print()

    # -----------------------------------------------------------------------
    # Phase 4: Node joins an FC (alice joins FC-energy as well as PHC-1)
    # -----------------------------------------------------------------------
    print("--- Phase 4: Alice joins FC-energy as a Functional Cell ---")
    fc_energy.add_node(alice)
    print(f"[node] alice PHC={alice.phc_id}  FCs={alice.fc_ids}")
    print()

    # -----------------------------------------------------------------------
    # Phase 5: FC limit enforcement — alice tries to join a 4th FC
    # -----------------------------------------------------------------------
    print("--- Phase 5: FC limit enforcement ---")
    fc_health  = Cell("FC-health",  "functional_cell")
    fc_health.add_node(carol)
    fc_health.add_node(grace)
    fc_health.add_node(hal)
    fc_health.add_node(alice)

    fc_edu = Cell("FC-education", "functional_cell")
    fc_edu.add_node(bob)
    fc_edu.add_node(dave)
    fc_edu.add_node(grace)
    fc_edu.add_node(alice)

    # alice is now in: PHC-1 (PHC), FC-energy (FC-1), FC-health (FC-2), FC-education (FC-3)
    print(f"[node] alice PHC={alice.phc_id}  FCs={alice.fc_ids}")

    # Attempting a 4th FC must raise an error
    fc_arts = Cell("FC-arts", "functional_cell")
    fc_arts.add_node(bob)
    fc_arts.add_node(carol)
    fc_arts.add_node(eve)
    try:
        fc_arts.add_node(alice)   # should raise
        print("[ERROR] expected ValueError was NOT raised")
    except ValueError as exc:
        print(f"[ok] FC limit correctly blocked: {exc}")
    print()

    # -----------------------------------------------------------------------
    # Phase 6: Cell forking — add nodes until PHC-1 exceeds 7 and fork
    # -----------------------------------------------------------------------
    print("--- Phase 6: Cell fork (PHC-1 exceeds 7 nodes) ---")
    # PHC-1 currently has: alice, bob, carol (3 nodes)
    # Add dave, eve, frank, grace, ivan to reach 8
    phc1.add_node(dave)
    phc1.add_node(eve)
    phc1.add_node(frank)
    phc1.add_node(grace)
    # Size is now 7 — at the cap; adding ivan should trigger a hard error
    try:
        phc1.add_node(ivan)
        print("[ERROR] expected ValueError was NOT raised at cap+1")
    except ValueError as exc:
        print(f"[ok] cap correctly enforced: {exc}")
    # Manually inject ivan to simulate a state that needs forking (bypass the guard)
    phc1._nodes.append(ivan)
    ivan._phc_id = phc1.cell_id
    print(f"[cell] PHC-1 now has {phc1.size} nodes (over limit) — forking…")
    phc1_left, phc1_right = phc1.fork()
    print(
        f"[cell] fork result: {phc1_left.cell_id} ({phc1_left.size} nodes), "
        f"{phc1_right.cell_id} ({phc1_right.size} nodes)"
    )
    print()

    # -----------------------------------------------------------------------
    # Phase 7: Unit formation from three Cells
    # -----------------------------------------------------------------------
    print("--- Phase 7: Unit formation ---")
    unit1 = Unit("Unit-1")
    unit1.add_cell(phc1_left)
    unit1.add_cell(phc1_right)
    unit1.add_cell(fc_energy)
    print(
        f"[unit] Unit-1 formed  cells={unit1.size}  "
        f"total_nodes={unit1.node_count()}  quorate={unit1.is_quorate()}"
    )
    print()

    # -----------------------------------------------------------------------
    # Phase 8: Bridge Contract between two cells in the Unit
    # -----------------------------------------------------------------------
    print("--- Phase 8: Bridge Contract ---")
    bc1 = BridgeContract(
        "BC-1",
        cell_ids=[phc1_left.cell_id, fc_energy.cell_id],
        description="Energy quota sharing between PHC-1-fork-0 and FC-energy",
        terms="FC-energy provides 2 kWh/day to PHC-1-fork-0 in exchange for labour credits",
        duration_seconds=604800,  # 7 days
    )
    unit1.add_bridge_contract(bc1)
    print()

    # -----------------------------------------------------------------------
    # Phase 9: Unit forking — add cells until Unit-1 exceeds 7 and fork
    # -----------------------------------------------------------------------
    print("--- Phase 9: Unit fork (Unit-1 exceeds 7 cells) ---")
    # Add more cells to reach 8
    unit1.add_cell(fc_health)
    unit1.add_cell(fc_edu)
    unit1.add_cell(fc_arts)
    # At 6 cells — add one more to reach the cap of 7
    extra_cell_a = Cell("FC-extra-a", "functional_cell")
    extra_cell_a._nodes.append(alice)  # just enough to be non-empty
    unit1.add_cell(extra_cell_a)
    # Now at cap — adding extra_cell_b must raise
    extra_cell_b = Cell("FC-extra-b", "functional_cell")
    extra_cell_b._nodes.append(bob)
    try:
        unit1.add_cell(extra_cell_b)
        print("[ERROR] expected ValueError was NOT raised at unit cap+1")
    except ValueError as exc:
        print(f"[ok] unit cap correctly enforced: {exc}")
    # Manually inject extra_cell_b and extra_cell_c to simulate the over-limit state
    extra_cell_c = Cell("FC-extra-c", "functional_cell")
    extra_cell_c._nodes.append(carol)
    unit1._cells.append(extra_cell_b)
    unit1._cells.append(extra_cell_c)
    print(f"[unit] Unit-1 now has {unit1.size} cells (over limit) — forking…")
    unit1_left, unit1_right = unit1.fork()
    print(
        f"[unit] fork result: {unit1_left.unit_id} ({unit1_left.size} cells), "
        f"{unit1_right.unit_id} ({unit1_right.size} cells)"
    )
    print()

    # -----------------------------------------------------------------------
    # Phase 10: Federation / Alliance (opt-in, time-boxed)
    # -----------------------------------------------------------------------
    print("--- Phase 10: Federation / Alliance ---")
    unit2 = Unit("Unit-2")
    unit2.add_cell(phc1_left)
    unit2.add_cell(fc_energy)
    unit2.add_cell(fc_health)

    # Form a Federation between two Units for cooperative energy management
    fed1 = FederationAlliance(
        "FED-1",
        fa_type="federation",
        units=[unit1_left, unit2],
        purpose="regional energy grid coordination",
        duration_seconds=2592000,  # 30 days
    )
    assert fed1.is_opt_in is True, "Federations must always be opt-in"

    # A third Unit opts in voluntarily
    unit3 = Unit("Unit-3")
    unit3.add_cell(fc_edu)
    unit3.add_cell(fc_arts)
    unit3.add_cell(extra_cell_a)
    fed1.add_unit(unit3)

    # Form a time-boxed Alliance for crisis response
    alliance1 = FederationAlliance(
        "ALLIANCE-crisis-mesh",
        fa_type="alliance",
        units=[unit1_right, unit2],
        purpose="Crisis Mesh — flood response coordination",
        duration_seconds=604800,  # 7 days — short-lived by design
    )
    assert not alliance1.is_expired(), "Alliance should not be expired immediately"
    print(f"[alliance] is_opt_in={alliance1.is_opt_in}  is_expired={alliance1.is_expired()}")
    print()

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    print("--- Summary ---")
    print(f"  PHC-1-fork-0  nodes : {[n.name for n in phc1_left.nodes]}")
    print(f"  PHC-1-fork-1  nodes : {[n.name for n in phc1_right.nodes]}")
    print(f"  FC-energy     nodes : {[n.name for n in fc_energy.nodes]}")
    print(f"  Unit-1-fork-0 cells : {[c.cell_id for c in unit1_left.cells]}")
    print(f"  Unit-1-fork-1 cells : {[c.cell_id for c in unit1_right.cells]}")
    print(f"  FED-1         units : {[u.unit_id for u in fed1.units]}")
    print(f"  Alice  PHC={alice.phc_id}  FCs={alice.fc_ids}")
    print(f"  Bob    PHC={bob.phc_id}   FCs={bob.fc_ids}")


if __name__ == "__main__":
    main()
