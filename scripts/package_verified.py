"""Package explicitly listed, hash-matching deliverables; never recurse a corpus."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def package(manifest, output):
    manifest, output = Path(manifest).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError('output exists; choose a new archive path')
    data = json.loads(manifest.read_text(encoding='utf-8-sig'))
    entries = data.get('files', [])
    if not entries:
        raise ValueError('empty files list')
    selected, names = [], {'manifest.json'}
    for entry in entries:
        raw = Path(entry['path'])
        if raw.is_absolute() or raw.drive or '..' in raw.parts:
            raise ValueError('file path must be relative and contained')
        source = (manifest.parent / raw).resolve()
        if not source.is_relative_to(manifest.parent) or not source.is_file():
            raise ValueError('missing or out-of-root file')
        name = raw.as_posix()
        folded = name.casefold()
        if folded in names or source in (manifest, output):
            raise ValueError('duplicate or reserved archive entry')
        names.add(folded)
        if entry.get('verified') is not True or not str(entry.get('evidence', '')).strip():
            raise ValueError('missing verification status or evidence')
        if sha256(source) != entry['sha256'].lower():
            raise ValueError(f'hash mismatch: {name}')
        selected.append((source, name))
    # Exclusive output, cleanup on failure. Read-back hash verifies archived bytes too.
    created = False
    try:
        with output.open('xb') as stream:
            created = True
            with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as archive:
                archive.writestr('manifest.json', json.dumps(data, ensure_ascii=False, indent=2))
                for source, name in selected:
                    archive.write(source, name)
        with zipfile.ZipFile(output) as archive:
            if archive.testzip() is not None:
                raise ValueError('archive CRC failure')
            for entry, (_, name) in zip(entries, selected):
                digest = hashlib.sha256()
                with archive.open(name) as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                        digest.update(chunk)
                if digest.hexdigest() != entry['sha256'].lower():
                    raise ValueError('archive hash mismatch')
    except Exception:
        if created:
            output.unlink(missing_ok=True)
        raise
    return len(selected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        count = package(args.manifest, args.output)
    except (ValueError, KeyError, OSError, zipfile.BadZipFile) as exc:
        parser.exit(1, f'Packaging failed: {exc}\n')
    print(f'Packaged {count} files: {args.output}')


if __name__ == '__main__':
    main()
