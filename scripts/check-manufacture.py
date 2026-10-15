#!/usr/bin/env python3
"""Check order-file consistency and regress the U1 stale-ground-fill short."""
import csv
import importlib.util
import hashlib
import json
import re
import zipfile
from pathlib import Path

spec = importlib.util.spec_from_file_location('common', Path(__file__).with_name('manufacture-common.py'))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
board = c.parse_sexpr((c.PCB_DIR / 'm5-pantilt.kicad_pcb').read_text())
fps = c.footprints(board)
full = c.electrical_refs(fps) - c.DNP
assert len(full) == 29, f'Unexpected full-assembly population: {len(full)}'

for suffix, expected in [('jlc', full - c.CUSTOMER), ('full-assembly', full)]:
    bom = list(csv.DictReader((c.OUTPUT / f'm5-pantilt-bom-{suffix}.csv').open()))
    placements = list(csv.DictReader((c.OUTPUT / f'm5-pantilt-cpl-{suffix}.csv').open()))
    bom_refs = [ref for row in bom for ref in row['Designator'].split(',')]
    assert len(bom_refs) == len(set(bom_refs)), 'Repeated BOM reference'
    assert set(bom_refs) == expected, f'{suffix}: incorrect BOM population'
    assert len(placements) == len(expected), f'{suffix}: duplicated/missing placements'
    assert {row['Designator'] for row in placements} == expected, f'{suffix}: BOM/CPL mismatch'
    for row in bom:
        for ref in row['Designator'].split(','):
            assert row['Footprint'] == fps[ref][1], f'{ref}: BOM footprint mismatch'
            assert row['LCSC Part #'] or ref in c.CUSTOMER, f'{ref}: missing part number'
        if suffix == 'full-assembly':
            assert int(row['Quantity per board']) == len(row['Designator'].split(','))
    for row in placements:
        ref = row['Designator']
        footprint = fps[ref]
        at = c.child(footprint, 'at')
        rotation = float(at[3]) if len(at) > 3 else 0
        assert abs(float(row['Mid X']) - float(at[1])) < 1e-6, f'{ref}: incorrect X'
        assert abs(float(row['Mid Y']) + float(at[2])) < 1e-6, f'{ref}: incorrect Y'
        assert abs((float(row['Rotation']) - rotation + 180) % 360 - 180) < 1e-6, f'{ref}: incorrect rotation'
        assert row['Layer'] == ('T' if c.child(footprint, 'layer')[1] == 'F.Cu' else 'B'), f'{ref}: incorrect side'
        assert row['Package'] == footprint[1].split(':')[-1], f'{ref}: incorrect package'
    print(f'{suffix}: {len(bom)} groups, {len(expected)} unique matching components')

# Ensure the placement exclusion did not delete the PCB's mechanical holes.
for ref, expected in {'Hole1': (146.8, 53.25), 'Hole2': (146.8, 96.95),
                      'Hole3': (103.2, 96.75), 'Hole4': (103.2, 53.05)}.items():
    fp = fps[ref]
    assert tuple(map(float, c.child(fp, 'at')[1:3])) == expected
    pads = c.children(fp, 'pad')
    assert len(pads) == 2 and all(p[2] == 'np_thru_hole' for p in pads)
    assert sorted(float(c.child(p, 'drill')[1]) for p in pads) == [2, 3]

# Sample interior points of every non-ground U1 pad, including the inner edge
# that overlapped GND before zone refilling. This is a regression, not a full DRC.
u1 = fps['U1']
assert u1[1] == 'm5-pantilt:SOIC-8_3.9x4.9mm_P1.27mm', u1[1]  # moved into the project library 2026-10
assert len(c.child(u1, 'at')) == 3 or float(c.child(u1, 'at')[3]) == 0
samples = []
for pad in c.children(u1, 'pad'):
    if c.child(pad, 'net')[2] == 'GND':
        continue
    at, size = c.child(pad, 'at'), c.child(pad, 'size')
    x = float(c.child(u1, 'at')[1]) + float(at[1])
    y = float(c.child(u1, 'at')[2]) + float(at[2])
    for dx in [-.95, -.5, 0, .5, .95]:
        for dy in [-.8, 0, .8]:
            samples.append((pad[1], (x + dx * float(size[1]) / 2, y + dy * float(size[2]) / 2)))
polygons = []
for zone in c.children(board, 'zone'):
    if c.child(zone, 'layer') == ['layer', 'F.Cu'] and c.child(zone, 'net_name') == ['net_name', 'GND']:
        polygons += [[tuple(map(float, xy[1:])) for xy in c.children(c.child(poly, 'pts'), 'xy')]
                     for poly in c.children(zone, 'filled_polygon')]
assert polygons, 'Missing filled front GND zone'
for pad, point in samples:
    assert not any(c.inside(point, polygon) for polygon in polygons), f'U1.{pad}: stale PCB ground fill overlaps pad at {point}'

# Independently inspect the exported positive GND regions, rather than assuming
# a corrected board means a corrected Gerber ZIP was exported.
source = (c.OUTPUT / 'gerbers/m5-pantilt-F_Cu.gtl').read_text()
assert '%FSLAX46Y46*%' in source, 'Update parser for changed Gerber coordinate format'
regions, contours, contour = [], [], []
x = y = 0
net = ''
positive = True
in_region = False
for line in source.splitlines():
    if line.startswith('%TO.N,'):
        net = line[len('%TO.N,'):-2]
    elif line == '%LPD*%':
        positive = True
    elif line == '%LPC*%':
        positive = False
    elif line == 'G36*':
        in_region = positive and net == 'GND'
        contours, contour = [], []
    elif line == 'G37*' and in_region:
        if contour:
            contours.append(contour)
        regions.append(contours)
        in_region = False
    elif in_region:
        match = re.fullmatch(r'(?:X(-?\d+))?(?:Y(-?\d+))?D0([12])\*', line)
        if match:
            if match[1] is not None:
                x = int(match[1]) / 1e6
            if match[2] is not None:
                y = -int(match[2]) / 1e6
            if match[3] == '2':
                if contour:
                    contours.append(contour)
                contour = []
            contour.append((x, y))
assert regions, 'Missing GND regions/attributes in Gerber'
for pad, point in samples:
    assert not any(sum(c.inside(point, polygon) for polygon in group) % 2 for group in regions), f'U1.{pad}: exported GND overlaps pad at {point}'
print(f'U1 PCB/Gerber ground-fill regression: {len(samples)} pad interior samples clear')

expected_layers = {'m5-pantilt-' + suffix for suffix in ['F_Cu.gtl', 'B_Cu.gbl', 'F_Mask.gts', 'B_Mask.gbs',
                   'F_Silkscreen.gto', 'B_Silkscreen.gbo', 'F_Paste.gtp', 'B_Paste.gbp', 'Edge_Cuts.gm1', 'PTH.drl', 'NPTH.drl']}
with zipfile.ZipFile(c.OUTPUT / 'm5-pantilt-gerbers-jlcpcb.zip') as archive:
    assert archive.testzip() is None
    assert set(archive.namelist()) == expected_layers
    assert all(archive.read(name) == (c.OUTPUT / 'gerbers' / name).read_bytes() for name in archive.namelist())
print('Mounting holes preserved; Gerber ZIP has 11 matching manufacturing files')

manifest = json.loads((c.PCB_DIR / 'manufacture/checks/manifest.json').read_text())
for name, expected in manifest['sha256'].items():
    assert hashlib.sha256((c.ROOT / name).read_bytes()).hexdigest() == expected, f'Changed source/output without regenerating checks: {name}'
for name, groups in [('drc.json', ('violations', 'unconnected_items', 'schematic_parity')),
                     ('parity.json', ('violations', 'unconnected_items', 'schematic_parity')),
                     ('erc.json', ('violations',))]:
    report = json.loads((c.PCB_DIR / 'manufacture/checks' / name).read_text())
    violations = c.erc_violations(report) if name == 'erc.json' else [v for group in groups for v in report[group]]
    assert not any(v.get('severity') == 'error' for v in violations), f'{name}: error findings'
print('DRC/ERC contain no errors; checked source/output hashes match')
