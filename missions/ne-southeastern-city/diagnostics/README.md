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

Interpretation:

| Southeastern level test | Southeastern content test | Result |
|---|---|---|
| Fails | Loads | Southeastern City level is rejected by the room validator |
| Loads | Fails | Something in the Southeastern mission content is rejected |
| Fails | Fails | More than one incompatibility exists |
| Loads | Loads | The combined mission triggers a validator interaction |
