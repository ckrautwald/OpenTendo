# RA2 modern resistor adapter — revision A prototype

Open `RA2-modern-adapter.kicad_pro` in KiCad 10, then open the schematic or PCB.

This stand-alone adapter replaces the electrical function of OpenTendo RA2 with
four Yageo RC0805FR-076K8L resistors (6.8 kΩ, 1%, 0805). The two-layer board is
13 × 7 mm and specifies 0.8 mm thickness. Components are on the front; pin numbers
and the common-pin marking are on the back. Each resistor body is nominally
2.0 × 1.25 mm. The hand-solder footprint uses 1.20 × 1.40 mm pads with their
centers 2.0 mm apart.

## Pin mapping

| Motherboard RA2 pin / adapter J1 pin | Connection |
| --- | --- |
| 1 | VCC, common end of all four resistors |
| 2 | OUT-0 through R1 |
| 3 | PPU-A13 through R2 |
| 4 | /OE1 through R3 |
| 5 | /OE2 through R4 |

The five mounting holes are on 2.54 mm centers, spanning 10.16 mm. Pin 1 has a
square pad. It must connect to RA2's original common pin; reversing the assembly
changes the circuit. The intended mounting is upright with five short formed
round wire leads, nominally 0.5 mm diameter. Lead lengths, bend geometry and
clearance have not been qualified. Do not assume 0.64 mm square header pins fit
the motherboard's nominal 0.8 mm drilled holes.

## Evidence and checks

The upstream schematic was fetched from
<https://github.com/Redherring32/OpenTendo/blob/master/Board%20Files/Motherboard.kicad_sch>.
GitHub reported file blob `fe3801181a59c6be0fa255e838c7241576a137fa` when inspected.
The source is in `../../Board Files/Motherboard.kicad_sch`; the upstream license
is at `../../LICENSE`. Its exported netlist establishes the mapping above.
The schematic assigns `Resistor_THT:R_Array_SIP5`; the locally installed KiCad
library defines its five holes at 2.54 mm pitch with 0.8 mm drills.

KiCad 10.0.8 reports zero ERC violations, zero DRC violations, zero unconnected
items, and zero schematic parity issues for this prototype. Reports and a netlist
are in `checks/`. These checks do not verify physical fit, lead mechanics, or
function in a powered NES. The complete upstream motherboard PCB could not be
retrieved with the connected file tool because it exceeded its size limit;
neighboring component clearance has therefore not been checked. Match the target
board revision before ordering parts or PCBs. No Gerber manufacturing release
has been prepared.

The resistor selection uses the manufacturer specification at
<https://www.yageogroup.com/component-documentation/download/specsheet/RC0805FR-076K8L>.
Distributor stock was not checked for this prototype. Wire lead and PCB suppliers
remain unselected; see `BOM.csv`.

`build_adapter.py` regenerates the files with the installed KiCad bundled Python
and libraries. Regeneration replaces hand edits. On this Mac:

```sh
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 build_adapter.py
```

The build script emits a KiCad wx initialization assertion in headless mode;
the saved files are independently parsed and checked by `kicad-cli`.

This project covers RA2 only. Diode, transistor, trimmer and connector replacement
designs have not been implemented or validated here.
