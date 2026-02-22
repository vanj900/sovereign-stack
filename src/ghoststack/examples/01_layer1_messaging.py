"""
Layer 1: Offline-First Messaging
=================================
Demonstrates SQLite-backed message queuing with an offline-then-online sync flow.

Components:
  - MeshDaemon     : placeholder for a real transport (cjdns / BATMAN / libp2p)
  - MessageQueue   : SQLite-backed per-node queue
  - sync_deliver   : transfers queued messages when a peer comes online

Run:
    python 01_layer1_messaging.py

Expected output:
    [queue] alice  queued msg → bob   : "Hello Bob, sync later!"
    [queue] alice  queued msg → bob   : "Offline message 2"
    [daemon] bob   is OFFLINE — messages held in alice's queue
    --- alice queue before sync ---
    id=1  from=alice  to=bob  payload=Hello Bob, sync later!  delivered=False
    id=2  from=alice  to=bob  payload=Offline message 2  delivered=False
    [daemon] bob   is now ONLINE
    [sync] delivering msg id=1 from alice → bob
    [inbox] bob    received: Hello Bob, sync later!
    [sync] delivering msg id=2 from alice → bob
    [inbox] bob    received: Offline message 2
    --- alice queue after sync ---
    id=1  from=alice  to=bob  payload=Hello Bob, sync later!  delivered=True
    id=2  from=alice  to=bob  payload=Offline message 2  delivered=True
    [done] 2 messages delivered
"""

import sqlite3
import tempfile
import os


# ---------------------------------------------------------------------------
# MeshDaemon – placeholder transport layer
# ---------------------------------------------------------------------------

class MeshDaemon:
    """
    Represents a node's transport handle.  In a real deployment this wraps a
    cjdns socket, a BATMAN neighbour table, or a libp2p host.  Here we just
    track online/offline state so the rest of the demo stays self-contained.
    """

    def __init__(self, node_id: str):
        self.node_id = node_id
        self._online = False

    def bring_online(self) -> None:
        self._online = True
        print(f"[daemon] {self.node_id:<6} is now ONLINE")

    def is_online(self) -> bool:
        return self._online

    def __repr__(self) -> str:
        state = "ONLINE" if self._online else "OFFLINE"
        return f"MeshDaemon(node={self.node_id}, state={state})"


# ---------------------------------------------------------------------------
# MessageQueue – SQLite-backed persistent queue
# ---------------------------------------------------------------------------

class MessageQueue:
    """
    A per-node SQLite queue.  Each row represents one envelope.

    Schema:
      id        – auto-incrementing primary key
      sender    – node_id of originator
      recipient – intended destination node_id
      payload   – message body (plain text for this prototype)
      delivered – 0 / 1 flag flipped after successful sync
    """

    def __init__(self, node_id: str, db_path: str):
        self.node_id = node_id
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                sender    TEXT    NOT NULL,
                recipient TEXT    NOT NULL,
                payload   TEXT    NOT NULL,
                delivered INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        self._conn.commit()

    def enqueue(self, recipient: str, payload: str) -> int:
        """Store a message for later delivery; returns its row id."""
        cur = self._conn.execute(
            "INSERT INTO messages (sender, recipient, payload) VALUES (?, ?, ?)",
            (self.node_id, recipient, payload),
        )
        self._conn.commit()
        print(f"[queue] {self.node_id:<6} queued msg → {recipient:<6}: \"{payload}\"")
        return cur.lastrowid

    def pending(self, recipient: str) -> list:
        """Return all un-delivered messages for a given recipient."""
        cur = self._conn.execute(
            "SELECT id, sender, recipient, payload FROM messages "
            "WHERE recipient = ? AND delivered = 0",
            (recipient,),
        )
        return cur.fetchall()

    def mark_delivered(self, msg_id: int) -> None:
        """Flip the delivered flag once a message has been handed off."""
        self._conn.execute(
            "UPDATE messages SET delivered = 1 WHERE id = ?", (msg_id,)
        )
        self._conn.commit()

    def all_messages(self) -> list:
        """Dump the full queue for inspection."""
        cur = self._conn.execute(
            "SELECT id, sender, recipient, payload, delivered FROM messages"
        )
        return cur.fetchall()

    def close(self) -> None:
        self._conn.close()


# ---------------------------------------------------------------------------
# Inbox – in-memory delivery target (simulates a live node's receive buffer)
# ---------------------------------------------------------------------------

class Inbox:
    """Collects messages delivered to a node during a sync session."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.messages: list = []

    def receive(self, msg_id: int, sender: str, payload: str) -> None:
        self.messages.append((msg_id, sender, payload))
        print(f"[inbox] {self.node_id:<6} received: {payload}")


# ---------------------------------------------------------------------------
# sync_deliver – the offline → online delivery routine
# ---------------------------------------------------------------------------

def sync_deliver(queue: MessageQueue, daemon: MeshDaemon, inbox: Inbox) -> int:
    """
    Transfer all pending messages to *inbox* if the destination daemon is online.

    Returns the number of messages delivered.
    """
    if not daemon.is_online():
        print(
            f"[daemon] {daemon.node_id:<6} is OFFLINE — messages held in "
            f"{queue.node_id}'s queue"
        )
        return 0

    pending = queue.pending(daemon.node_id)
    delivered_count = 0
    for msg_id, sender, recipient, payload in pending:
        print(f"[sync] delivering msg id={msg_id} from {sender} → {recipient}")
        inbox.receive(msg_id, sender, payload)
        queue.mark_delivered(msg_id)
        delivered_count += 1
    return delivered_count


# ---------------------------------------------------------------------------
# Helper – pretty-print queue contents
# ---------------------------------------------------------------------------

def print_queue(queue: MessageQueue, label: str) -> None:
    print(f"\n--- {label} ---")
    for row in queue.all_messages():
        msg_id, sender, recipient, payload, delivered = row
        status = "True" if delivered else "False"
        print(
            f"  id={msg_id}  from={sender}  to={recipient}  "
            f"payload={payload}  delivered={status}"
        )
    print()


# ---------------------------------------------------------------------------
# Main demo
# ---------------------------------------------------------------------------

def main() -> None:
    # Use a temp file so the demo is self-cleaning
    db_fd, db_path = tempfile.mkstemp(suffix=".db", prefix="ghoststack_layer1_")
    os.close(db_fd)

    try:
        # --- Setup ---
        alice_queue = MessageQueue("alice", db_path)
        bob_daemon = MeshDaemon("bob")
        bob_inbox = Inbox("bob")

        # --- Alice queues messages while Bob is offline ---
        alice_queue.enqueue("bob", "Hello Bob, sync later!")
        alice_queue.enqueue("bob", "Offline message 2")

        # Attempt delivery — Bob is still offline
        sync_deliver(alice_queue, bob_daemon, bob_inbox)

        print_queue(alice_queue, "alice queue before sync")

        # --- Bob comes online ---
        bob_daemon.bring_online()

        # Retry sync — now messages flow
        count = sync_deliver(alice_queue, bob_daemon, bob_inbox)

        print_queue(alice_queue, "alice queue after sync")
        print(f"[done] {count} messages delivered")

        alice_queue.close()

    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


if __name__ == "__main__":
    main()
