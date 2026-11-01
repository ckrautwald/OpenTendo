"""Rebuild the RA2 prototype with KiCad's bundled Python (pcbnew)."""
from pathlib import Path
import json
import uuid
import pcbnew as p

ROOT = Path(__file__).resolve().parent
SUPPORT = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport')
NAME = 'RA2-modern-adapter'
RFP = 'R_0805_2012Metric_Pad1.20x1.40mm_HandSolder'
JFP = 'SIP5_WireLeads_P2.54mm'
uid = lambda: str(uuid.uuid4())
sheet = uid()
ids = {ref: uid() for ref in ['J1', 'R1', 'R2', 'R3', 'R4']}

def embedded(lib, name):
    s = (SUPPORT / 'symbols' / (lib + '.kicad_sym')).read_text()
    start = s.index('\n\t(symbol "' + name + '"')
    end = s.find('\n\t(symbol "', start + 1)
    part = s[start:end if end != -1 else s.rfind('\n)')]
    return part.replace('(symbol "' + name + '"', '(symbol "' + lib + ':' + name + '"', 1)

def prop(name, value, x, y, hide=False):
    return f'(property "{name}" "{value}" (at {x} {y} 0) (effects (font (size 1.27 1.27))'+(' (hide yes)' if hide else '')+'))'

def symbol(lib, ref, value, x, y, footprint, n):
    out = f'(symbol (lib_id "{lib}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{ids[ref]}")'
    out += prop('Reference', ref, x+5.08, y-2.54)
    out += prop('Value', value, x+6.35, y+1.27)
    out += prop('Footprint', footprint, x, y, True)
    if ref.startswith('R'):
        out += prop('MPN','RC0805FR-076K8L',x,y,True)
        out += prop('Datasheet','https://www.yageogroup.com/component-documentation/download/specsheet/RC0805FR-076K8L',x,y,True)
    for i in range(1,n+1):
        out += f'(pin "{i}" (uuid "{uid()}"))'
    out += f'(instances (project "{NAME}" (path "/{sheet}" (reference "{ref}") (unit 1)))))'
    return out

def wire(x,y,a,b):
    return f'(wire (pts (xy {x} {y}) (xy {a} {b})) (stroke (width 0) (type default)) (uuid "{uid()}"))'

def label(name,x,y):
    return f'(label "{name}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{uid()}"))'

parts=[f'(kicad_sch (version 20250114) (generator "eeschema") (uuid "{sheet}") (paper "A5")',
       '(title_block (title "OpenTendo RA2 - four-resistor adapter") (rev "A-prototype") (comment 1 "13 x 7 mm; validate physical fit before fabrication"))',
       '(lib_symbols '+embedded('Device','R')+embedded('Connector_Generic','Conn_01x05')+')']
signals=['OUT-0','PPU-A13','~{OE1}','~{OE2}']
for i, net in enumerate(signals):
    x=76.2+20.32*i
    parts += [symbol('Device:R',f'R{i+1}','6.8k',x,76.2,'Resistor_SMD:'+RFP,2),
              wire(x,72.39,x,68.58),label('VCC',x,68.58),wire(x,80.01,x,85.09),label(net,x,85.09)]
parts.append(symbol('Connector_Generic:Conn_01x05','J1','RA2_WIRE_LEADS',76.2,111.76,'RA2_Adapter:'+JFP,5))
for i, net in enumerate(['VCC']+signals):
    y=106.68+2.54*i
    parts += [wire(55.88,y,71.12,y),label(net,55.88,y)]
parts += [f'(text "Prototype: 4 x 6.8k, 1%, 0805. Pin 1 = VCC/common.\\nFit with 0.5 mm round wire leads, not 0.64 mm square headers.\\nElectrical pinout checked against upstream schematic; mechanical fit unverified." (at 111.76 134.62 0) (effects (font (size 1.27 1.27))) (uuid "{uid()}"))',
          '(sheet_instances (path "/" (page "1")))', '(embedded_fonts no))']
(ROOT/(NAME+'.kicad_sch')).write_text('\n'.join(parts)+'\n')

board=p.BOARD()
io=p.PCB_IO_KICAD_SEXPR()
board.GetDesignSettings().SetCopperLayerCount(2)
board.GetDesignSettings().SetBoardThickness(p.FromMM(0.8))
v=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
nets={}
for name in ['VCC']+signals:
    net=p.NETINFO_ITEM(board,'/'+name);board.Add(net);nets[name]=net

# Five round wire leads fit the 0.8 mm holes of the library's SIP5 footprint.
j=p.FOOTPRINT(board)
j.SetFPID(p.LIB_ID('RA2_Adapter',JFP))
j.SetReference('J1');j.SetValue('RA2_WIRE_LEADS')
j.SetAttributes(p.FP_THROUGH_HOLE)
for i,name in enumerate(['VCC']+signals):
    pad=p.PAD(j);pad.SetNumber(str(i+1));pad.SetAttribute(p.PAD_ATTRIB_PTH)
    pad.SetShape(p.PAD_SHAPE_RECT if i==0 else p.PAD_SHAPE_CIRCLE)
    layers=p.LSET()
    for layer in [p.F_Cu,p.B_Cu,p.F_Mask,p.B_Mask]:layers.AddLayer(layer)
    pad.SetSize(v(1.5,1.5));pad.SetDrillSize(v(.8,.8));pad.SetLayerSet(layers)
    pad.SetPosition(v(i*2.54,0));pad.SetNet(nets[name]);j.Add(pad)
j.Reference().SetVisible(False);j.Value().SetVisible(False)
lib=ROOT/'RA2_Adapter.pretty';lib.mkdir(exist_ok=True)
io.FootprintSave(str(lib),j)
j.SetPosition(v(51.42,56));j.SetPath(p.KIID_PATH('/'+sheet+'/'+ids['J1']));board.Add(j)

def track(x,y,a,b,name):
    t=p.PCB_TRACK(board);t.SetStart(v(x,y));t.SetEnd(v(a,b));t.SetWidth(p.FromMM(.25));t.SetLayer(p.F_Cu);t.SetNet(nets[name]);board.Add(t)

def text(s,x,y,layer=p.F_SilkS,size=.65):
    t=p.PCB_TEXT(board);t.SetText(s);t.SetPosition(v(x,y));t.SetTextSize(v(size,size));t.SetTextThickness(p.FromMM(.12));t.SetLayer(layer);board.Add(t)

track(51.42,56,51.42,50.8,'VCC');track(51.42,50.8,61.58,50.8,'VCC')
for i,name in enumerate(signals):
    x=53.96+2.54*i
    fp=io.FootprintLoad(str(SUPPORT/'footprints'/'Resistor_SMD.pretty'),RFP)
    fp.SetReference(f'R{i+1}');fp.SetValue('6.8k');fp.SetFPID(p.LIB_ID('Resistor_SMD',RFP))
    fp.SetOrientationDegrees(270);fp.SetPosition(v(x,53))
    fp.SetPath(p.KIID_PATH('/'+sheet+'/'+ids[f'R{i+1}']))
    fp.Reference().SetVisible(False);fp.Value().SetVisible(False)
    fp.SetField('MPN','RC0805FR-076K8L');fp.GetField('MPN').SetVisible(False)
    fp.SetField('Datasheet','https://www.yageogroup.com/component-documentation/download/specsheet/RC0805FR-076K8L');fp.GetField('Datasheet').SetVisible(False)
    for pad in fp.Pads():pad.SetNet(nets['VCC' if pad.GetNumber()=='1' else name])
    board.Add(fp)
    coords={pad.GetNumber():pad.GetPosition() for pad in fp.Pads()}
    for number,padpos in coords.items():
        print(fp.GetReference(),number,p.ToMM(padpos.x),p.ToMM(padpos.y))
    a=coords['1'];b=coords['2']
    track(p.ToMM(a.x),p.ToMM(a.y),x,50.8,'VCC')
    track(p.ToMM(b.x),p.ToMM(b.y),x,56,name)
    text(str(i+2),x,54.5,p.B_SilkS,.8)
text('1',51.42,54.5,p.B_SilkS,.8)
text('RA2 4x6K8 A',56.5,51.8,p.B_SilkS,.8)
text('VCC',51.6,53,p.B_SilkS,.8)
# Back silkscreen must read correctly from the rear.
for item in board.GetDrawings():
    if isinstance(item,p.PCB_TEXT) and item.GetLayer()==p.B_SilkS:item.SetMirrored(True)
for x,y,a,b in [(50,50,63,50),(63,50,63,57),(63,57,50,57),(50,57,50,50)]:
    edge=p.PCB_SHAPE();edge.SetShape(p.SHAPE_T_SEGMENT);edge.SetStart(v(x,y));edge.SetEnd(v(a,b));edge.SetLayer(p.Edge_Cuts);edge.SetWidth(p.FromMM(.05));board.Add(edge)
p.PCB_IO_KICAD_SEXPR().SaveBoard(str(ROOT/(NAME+'.kicad_pcb')),board)
project={'meta':{'filename':NAME+'.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':.2,'min_track_width':.2,'min_copper_edge_clearance':.25,'min_through_hole_diameter':.3}}},'net_settings':{'classes':[{'name':'Default','clearance':.2,'track_width':.25,'via_diameter':.6,'via_drill':.3,'bus_width':12,'line_style':0,'microvia_diameter':.3,'microvia_drill':.1,'pcb_color':'rgba(0, 0, 0, 0.000)','schematic_color':'rgba(0, 0, 0, 0.000)','wire_width':6}],'meta':{'version':3}}}
(ROOT/(NAME+'.kicad_pro')).write_text(json.dumps(project,indent=2)+'\n')
(ROOT/'fp-lib-table').write_text('(fp_lib_table (version 7)\n (lib (name "RA2_Adapter") (type "KiCad") (uri "${KIPRJMOD}/RA2_Adapter.pretty") (options "") (descr "Prototype SIP wire lead interface"))\n (lib (name "Resistor_SMD") (type "KiCad") (uri "${KICAD10_FOOTPRINT_DIR}/Resistor_SMD.pretty") (options "") (descr "KiCad standard resistors"))\n)\n')
(ROOT/'sym-lib-table').write_text('(sym_lib_table (version 7)\n (lib (name "Device") (type "KiCad") (uri "${KICAD10_SYMBOL_DIR}/Device.kicad_sym") (options "") (descr ""))\n (lib (name "Connector_Generic") (type "KiCad") (uri "${KICAD10_SYMBOL_DIR}/Connector_Generic.kicad_sym") (options "") (descr ""))\n)\n')
(ROOT/'BOM.csv').write_text('Reference,Quantity,Manufacturer,Part number,Description\n"R1 R2 R3 R4",4,Yageo,RC0805FR-076K8L,"6.8 kohm 1% 0805 resistor"\nJ1,5,Unselected,Unselected,"0.5 mm diameter round tinned copper wire leads cut to length; qualify mechanically"\nPCB,1,Unselected,RA2-modern-adapter,"13 x 7 mm 2-layer 0.8 mm prototype board"\n')
print(ROOT/(NAME+'.kicad_pro'))
