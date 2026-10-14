#!/usr/bin/env python3
"""Rebuild serial-route manufacturing outputs; preserve all historical PDFs."""
import argparse
import csv
import importlib.util
import hashlib
import json
import os
import subprocess
import shutil
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from collections import OrderedDict
from pathlib import Path

spec = importlib.util.spec_from_file_location('common', Path(__file__).with_name('manufacture-common.py'))
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--kicad-cli', default='kicad-cli')
args = parser.parse_args()
board = common.PCB_DIR / 'm5-pantilt.kicad_pcb'
schematic = common.PCB_DIR / 'm5-pantilt.kicad_sch'
out = common.OUTPUT
reports = common.PCB_DIR / 'manufacture/checks'
reports.mkdir(exist_ok=True)
settings = json.loads((out / 'assembly-parts.json').read_text())


def run(*command):
    preferences = common.PCB_DIR / 'm5-pantilt.kicad_prl'
    original_preferences = preferences.read_bytes() if preferences.exists() else None
    try:
        subprocess.run([args.kicad_cli, *map(str, command)], check=True, cwd=common.PCB_DIR)
    finally:
        # The CLI may update local UI preferences; manufacturing must not.
        if original_preferences is not None:
            preferences.write_bytes(original_preferences)
        elif preferences.exists():
            preferences.unlink()


def check_drc(report):
    if 'violations' not in report or 'unconnected_items' not in report:
        raise ValueError('Unsupported DRC report schema')
    errors = [v for group in ('violations', 'unconnected_items', 'schematic_parity')
              for v in report.get(group, []) if v.get('severity') == 'error']
    if errors:
        raise SystemExit(f'DRC has {len(errors)} errors; no manufacturing files exported. See {reports / "drc.json"}')


# Refill with the native engine in an isolated copy. Transfer only zone fills
# back, preserving the original KiCad 7 format, holes, pad nets and routing.
with tempfile.TemporaryDirectory(prefix='stackchan-zone-refill-') as tmp:
    work = Path(tmp)
    target = work / board.name
    shutil.copy2(board, target)
    for name in ('m5-pantilt.kicad_pro', 'fp-lib-table'):
        shutil.copy2(common.PCB_DIR / name, work / name)
    (work / 'm5-pantilt.pretty').symlink_to(common.PCB_DIR / 'm5-pantilt.pretty', target_is_directory=True)
    run('pcb', 'drc', '--refill-zones', '--save-board', '--format', 'json',
        '--severity-all', '--output', reports / 'drc.json', target)
    check_drc(json.loads((reports / 'drc.json').read_text()))
    original = board.read_text()
    board.write_text(common.copy_native_zone_fills(original, target.read_text()))
# Check the actual preserved-format board, with its saved fills, before export.
run('pcb', 'drc', '--format', 'json', '--severity-all', '--output', reports / 'drc.json', board)
check_drc(json.loads((reports / 'drc.json').read_text()))
run('pcb', 'drc', '--schematic-parity', '--format', 'json', '--severity-all',
    '--output', reports / 'parity.json', board)
check_drc(json.loads((reports / 'parity.json').read_text()))
run('sch', 'erc', '--format', 'json', '--severity-all', '--output', reports / 'erc.json', schematic)
# Stop on ERC errors too; warnings remain visible in the saved report.
erc = json.loads((reports / 'erc.json').read_text())
if any(v.get('severity') == 'error' for v in common.erc_violations(erc)):
    raise SystemExit('ERC errors must be resolved before exporting manufacturing files')
with tempfile.TemporaryDirectory(prefix='stackchan-manufacture-') as tmp:
    generated = Path(tmp)
    gerbers = generated / 'gerbers'
    gerbers.mkdir()
    run('pcb', 'export', 'gerbers', '--output', str(gerbers) + os.sep, board)
    # No --generate-map: existing drill-map PDFs remain untouched.
    run('pcb', 'export', 'drill', '--excellon-separate-th', '--output', str(gerbers) + os.sep, board)
    run('pcb', 'export', 'pos', '--format', 'csv', '--units', 'mm', '--side', 'both',
        '--output', generated / 'pos-both.csv', board)
    run('sch', 'export', 'netlist', '--format', 'kicadxml',
        '--output', generated / 'python-bom.csv', schematic)
    fps = common.footprints(common.parse_sexpr(board.read_text()))
    refs = common.electrical_refs(fps) - common.DNP
    components = {c.attrib['ref']: c for c in ET.parse(generated / 'python-bom.csv').findall('./components/comp')}
    positions = {p['Ref']: p for p in csv.DictReader((generated / 'pos-both.csv').open())}
    if not refs <= components.keys() or not refs <= positions.keys():
        raise SystemExit('Missing electrical component in exported netlist/coordinates')

    def write_pair(suffix, selected, full=False):
        groups = OrderedDict()
        for ref in sorted(selected, key=common.natural_ref):
            comp = components[ref]
            lcsc = next((field.text for field in comp.findall('./fields/field') if field.attrib['name'] == 'LCSC'), '') or ''
            lcsc = settings['lcsc_overrides'].get(ref, lcsc)
            package = fps[ref][1]
            smd = 'smd' in common.child(fps[ref], 'attr')[1:]
            supplied = ref in common.CUSTOMER
            if not lcsc and not supplied:
                raise SystemExit(f'Missing LCSC part: {ref}')
            assembly = ('SMD' if smd else 'THT') + ('(客户供料)' if supplied else '(可贴)' if smd else '(插件，需单独安排)')
            value = comp.findtext('value')
            key = (value, package, lcsc, assembly, settings['customer_parts'].get(ref, {}).get('spec', ''))
            groups.setdefault(key, []).append(ref)
        fields = ['Comment', 'Designator', 'Footprint', 'LCSC Part #', 'Assembly']
        if full:
            fields += ['Quantity per board', 'Purchase specification']
        with (out / f'm5-pantilt-bom-{suffix}.csv').open('w', newline='') as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(fields)
            for (value, package, lcsc, assembly, purchase), group in groups.items():
                row = [value, ','.join(group), package, lcsc, assembly]
                if full:
                    row += [len(group), purchase]
                writer.writerow(row)
        with (out / f'm5-pantilt-cpl-{suffix}.csv').open('w', newline='') as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(['Designator', 'Val', 'Package', 'Mid X', 'Mid Y', 'Rotation', 'Layer'])
            for ref in sorted(selected, key=common.natural_ref):
                position = positions[ref]
                writer.writerow([ref, position['Val'], position['Package'], position['PosX'],
                                 position['PosY'], position['Rot'], 'T' if position['Side'] == 'top' else 'B'])
        print(f'{suffix}: {len(groups)} BOM groups / {len(selected)} components')

    write_pair('jlc', refs - common.CUSTOMER)
    write_pair('full-assembly', refs, full=True)
    for source in gerbers.iterdir():
        (out / 'gerbers' / source.name).write_bytes(source.read_bytes())
    (out / 'cpl/pos-both.csv').write_bytes((generated / 'pos-both.csv').read_bytes())
    (out / 'python-bom.csv').write_bytes((generated / 'python-bom.csv').read_bytes())
    layers = ['F_Cu.gtl', 'B_Cu.gbl', 'F_Mask.gts', 'B_Mask.gbs', 'F_Silkscreen.gto',
              'B_Silkscreen.gbo', 'F_Paste.gtp', 'B_Paste.gbp', 'Edge_Cuts.gm1', 'PTH.drl', 'NPTH.drl']
    with zipfile.ZipFile(out / 'm5-pantilt-gerbers-jlcpcb.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for layer in layers:
            name = 'm5-pantilt-' + layer
            # Fixed archive timestamps avoid unrelated ZIP changes on regeneration.
            info = zipfile.ZipInfo(name, (2026, 10, 14, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, (gerbers / name).read_bytes())
version = subprocess.check_output([args.kicad_cli, 'version'], text=True).strip()
# Normalize source paths so committed reports are portable across checkouts.
for report_path in (reports / 'drc.json', reports / 'erc.json', reports / 'parity.json'):
    report = json.loads(report_path.read_text())
    if 'source' in report:
        report['source'] = Path(report['source']).name
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
netlist = ET.parse(out / 'python-bom.csv')
netlist.find('./design/source').text = schematic.name
netlist.write(out / 'python-bom.csv', encoding='UTF-8', xml_declaration=True)
files = [board, schematic, reports / 'drc.json', reports / 'erc.json', reports / 'parity.json']
files += [common.PCB_DIR / name for name in ('m5-pantilt.kicad_pro', 'fp-lib-table', 'sym-lib-table')]
files += list((common.PCB_DIR / 'm5-pantilt.pretty').glob('*.kicad_mod'))
files += [f for f in out.rglob('*') if f.is_file() and f.suffix in {'.csv', '.zip', '.json', '.gtl', '.gbl', '.gts', '.gbs', '.gto', '.gbo', '.gtp', '.gbp', '.gm1', '.drl'}]
manifest = {'kicad_version': version, 'sha256': {str(f.relative_to(common.ROOT)): hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(set(files))}}
(reports / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
subprocess.run(['python3', str(common.ROOT / 'scripts/check-manufacture.py')], check=True)
