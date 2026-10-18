# Southeastern City custom-room diagnostics

These files isolate failures in War Thunder's remote custom-room validator.
They are not intended as playable layouts.

- `archipelago-content-southeastern-level.blk` is the known-working
  Archipelago mission with only its level changed to Southeastern City.
- `southeastern-content-archipelago-level.blk` is the flattened Southeastern
  City mission with only its level changed to the known-working Archipelago.
- `southeastern-logic-archipelago-units.blk` keeps the Southeastern level,
  triggers, objectives, areas, and waypoints but substitutes the complete
  known-working Archipelago `units` block. Every Southeastern target name is
  present in that block.
- `southeastern-nomesh-replaced.blk` is the complete Southeastern mission with
  only the two `nt_assembly_area_nomesh` unit classes replaced by the standard
  `nt_assembly_area_foundation` class used by the working mission.
- `southeastern-objects-01-50.blk` and
  `southeastern-objects-51-98.blk` split the Southeastern map-object
  definitions across two otherwise working units blocks.
- `southeastern-objects-01-25.blk` and
  `southeastern-objects-26-50.blk` bisect the failing first half again.

Interpretation:

| Southeastern level test | Southeastern content test | Result |
|---|---|---|
| Fails | Loads | Southeastern City level is rejected by the room validator |
| Loads | Fails | Something in the Southeastern mission content is rejected |
| Fails | Fails | More than one incompatibility exists |
| Loads | Loads | The combined mission triggers a validator interaction |
