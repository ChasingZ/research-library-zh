"""Heuristic integrity audit for aligned source/target JSONL, using stdlib only."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

MARKER = re.compile(r'XXPH\d+XX|@\d+@')
# Latin-aware boundaries allow adjacent Chinese; final punctuation is not a decimal.
NUMBER = re.compile(
    r'(?<![A-Za-z0-9_.])[-+]?\d+(?:,\d{3})*(?:\.\d+)?'
    r'(?:[eE][-+]?\d+)?(?:[BTMKk]|%)?(?![A-Za-z0-9_]|\.\d)')
ECHO = ('只输出译文', '保留所有占位符', '你是一名专业翻译', '请提供需要翻译')


def numbers(text):
    return Counter(NUMBER.findall(MARKER.sub('', text)))


def audit(unit):
    source, target = unit['source'], unit['target']
    issues = []
    if Counter(MARKER.findall(source)) != Counter(MARKER.findall(target)):
        issues.append('placeholder_multiset_mismatch')
    if numbers(source) != numbers(target):
        issues.append('visible_number_mismatch')
    if source.strip() and not target.strip():
        issues.append('empty_target')
    if unit.get('verbatim') and source != target:
        issues.append('verbatim_changed')
    if any(phrase in target and phrase not in source for phrase in ECHO):
        issues.append('possible_instruction_echo')
    return {'id': unit['id'], 'issues': issues}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('units', type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    units = [json.loads(line) for line in args.units.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    ids = [unit['id'] for unit in units]
    if len(ids) != len(set(ids)):
        parser.error('duplicate unit IDs')
    checks = [audit(unit) for unit in units]
    flags = [check for check in checks if check['issues']]
    args.report.write_text(json.dumps({'units': len(units), 'flags': flags,
        'scope': 'Heuristic integrity checks; does not certify semantic quality or completeness.'},
        ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{len(units)} units; {len(flags)} flagged')
    return 1 if flags else 0


if __name__ == '__main__':
    raise SystemExit(main())
