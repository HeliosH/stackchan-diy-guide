"""Read embedded KiCad geometry without requiring a local pcbnew installation."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PCB_DIR = ROOT / 'pcb/m5-pantilt-v1.0'
OUTPUT = PCB_DIR / 'manufacture/jlcpcb'
DNP = {'R9', 'R10', 'R11', 'R12'}
CUSTOMER = {'J1', 'J2', 'SW1'}


def parse_sexpr(source):
    tokens = iter(re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+', source))

    def read(token):
        if token != '(':
            return json.loads(token) if token.startswith('"') else token
        items = []
        for token in tokens:
            if token == ')':
                return items
            items.append(read(token))
        raise ValueError('Unclosed KiCad expression')

    return read(next(tokens))


def children(node, name):
    return [item for item in node if isinstance(item, list) and item and item[0] == name]


def child(node, name):
    return next(iter(children(node, name)), [])


def footprints(board):
    result = {}
    for footprint in children(board, 'footprint'):
        references = [p[2] for p in children(footprint, 'property') if p[1] == 'Reference']
        references += [p[2] for p in children(footprint, 'fp_text') if p[1] == 'reference']
        if references:
            result[references[0]] = footprint
    return result


def electrical_refs(items):
    return {ref for ref in items if re.fullmatch(r'(?:C|D|J|Q|R|SW|U)\d+', ref)}


def natural_ref(ref):
    prefix, number = re.fullmatch(r'([A-Z]+)(\d+)', ref).groups()
    return prefix, int(number)


def inside(point, polygon):
    x, y = point
    result = False
    for index, (a, b) in enumerate(polygon):
        u, v = polygon[index - 1]
        if ((b > y) != (v > y)) and x < (u - a) * (y - b) / (v - b) + a:
            result = not result
    return result


def expression_spans(source, name):
    """Find complete expressions while respecting quoted strings and nesting."""
    stack = []
    result = []
    for match in re.finditer(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+', source):
        token = match.group()
        if token == '(':
            stack.append([match.start(), None])
        elif token == ')':
            start, head = stack.pop()
            if head == name:
                result.append((start, match.end()))
        elif stack and stack[-1][1] is None:
            stack[-1][1] = token
    return sorted(result)


def copy_native_zone_fills(original, refilled):
    """Copy native KiCad fills without upgrading unrelated legacy PCB geometry.

    KiCad 10's save operation upgrades the entire PCB format. Both formats use
    the same filled_polygon layer/pts/island records, so retain the original
    board and zone settings and transfer only the recalculated copper polygons.
    The caller must run DRC again on the actual resulting board.
    """
    native = {}
    for start, end in expression_spans(refilled, 'zone'):
        source = refilled[start:end]
        node = parse_sexpr(source)
        key = (child(node, 'layer')[1], child(node, 'net')[1])
        polygons = []
        for first, last in expression_spans(source, 'filled_polygon'):
            polygon = source[first:last]
            fields = {item[0] for item in parse_sexpr(polygon)[1:] if isinstance(item, list)}
            if not fields <= {'layer', 'pts', 'island'}:
                raise ValueError(f'Unsupported native fill fields: {fields}')
            polygons.append(polygon)
        if not polygons:
            raise ValueError(f'No native fill for zone {key}')
        if key in native:
            raise ValueError(f'Ambiguous zone key: {key}')
        native[key] = polygons
    replacements = []
    for start, end in expression_spans(original, 'zone'):
        source = original[start:end]
        node = parse_sexpr(source)
        key = (child(node, 'layer')[1], child(node, 'net_name')[1])
        polygons = native.pop(key)
        for first, last in reversed(expression_spans(source, 'filled_polygon')):
            source = source[:first] + source[last:]
        source = source.rstrip()[:-1].rstrip() + '\n    ' + '\n    '.join(polygons) + '\n  )'
        replacements.append((start, end, source))
    if native or len(replacements) != 2:
        raise ValueError('Expected the two original front/back GND zones')
    for start, end, replacement in reversed(replacements):
        original = original[:start] + replacement + original[end:]
    return original


def erc_violations(report):
    # ERC v1 stores violations under sheets; DRC stores them at the top level.
    if 'sheets' not in report:
        raise ValueError('Unsupported ERC report schema')
    return [violation for sheet in report['sheets'] for violation in sheet['violations']]
