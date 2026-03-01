"""
src/energy — Energy Coupler v1 (AC-Coupled Design)
====================================================
Coupler firmware for a 3-7 node sovereign cell sharing a 240 V AC bus.

Philosophy: Flow Over Containment.  Every node stays sovereign.
Sharing is optional, never mandatory.  If the coupler dies, nobody goes dark.

Modules:
  modbus_maps      — Modbus register maps for EG4 / Sol-Ark / Victron inverters
  ghostbrain       — Demand forecasting + grid-former election
  coupler          — Per-node coupler firmware (contactor, metering, safety)
  integrity_chain  — Energy transfer deed logging (hash-chain / Integrity Chain)
"""
