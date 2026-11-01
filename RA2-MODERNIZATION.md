# RA2 motherboard integration

This branch replaces the motherboard's RA2 bussed resistor network with four
Yageo RC0805FR-076K8L resistors: 6.8 kΩ, 1%, 0805. These mount directly on the
motherboard. The separate adapter project in `adapters/ra2/` remains an earlier
prototype and is not needed to assemble this motherboard revision.

| New resistor | Common end | Signal end | Former RA2 pin |
| --- | --- | --- | --- |
| R20 | VCC | OUT-0 | 2 |
| R21 | VCC | PPU-A13 | 3 |
| R22 | VCC | /OE1 | 4 |
| R23 | VCC | /OE2 | 5 |

The original RA2 pin 1 supplied the common VCC connection. All four new pin-1
pads connect to that supply; pin 2 of each resistor connects to its signal.
The resistors use the prototype's KiCad 0805 hand-solder footprint. R23 is offset
to clear OUT-1 routing. Local OUT-0 and VCC routing uses additional vias; the
adjacent OE2 trace is displaced slightly for clearance. The old SIP holes are
removed. No adapter, header, or wire leads are required.

Open `Board Files/Motherboard.kicad_pro` in KiCad 10. The PCB was saved by KiCad
10.0.8 when refilling copper zones, so its diff also includes the automatic board
format upgrade. The motherboard thickness remains 1.6 mm, rather than the
adapter prototype's 0.8 mm. `BOM/BOM.csv`, `BOM/README.md`, and the interactive
assembly view reflect R20–R23. Distributor stock has not been rechecked.

## Validation

Compared with the pre-integration branch commit
`4c21873` (upstream motherboard files identical to `3bd0b0b`):

- Exported schematic connectivity is identical after expanding the original RA2
  into the four individual resistors. All 129 net node sets match.
- PCB DRC after zone refill: 109 findings versus 113 previously, with no new
  findings by check type and involved item UUIDs.
- Unconnected PCB items: zero before and after.
- Schematic ERC: 74 findings before and after, with no new findings by check
  type and involved item UUIDs.
- Schematic parity: one existing extra `REF**` footprint, unrelated to RA2.

The pre-existing whole-board findings remain unresolved. This is a design
prototype, not a fabrication release; physical assembly and powered operation
have not been tested. Archived reports are in `validation/ra2/`.

The regenerated interactive BOM omits the embedded bitmap artwork from its
display-only input because the headless parser cannot decode that image. The
actual motherboard PCB retains the artwork. Footprints, pads, tracks, nets, and
zones in the assembly view come from the modified board.
