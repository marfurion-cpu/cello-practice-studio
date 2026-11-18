#!/usr/bin/env python3
"""Offline integrity/path gate; not musical, security or browser certification."""
import hashlib, json, re, stat, sys, zipfile
from pathlib import Path, PurePosixPath

def validate(archive, manifest, archive_names):
    assert sorted(archive_names) == ['site.zip'], 'Exactly one archive named site.zip is required'
    assert manifest['schema_version'] == 1
    assert re.fullmatch(r'[0-9a-f]{40}', manifest['baseline_commit'])
    assert hashlib.sha256(archive).hexdigest() == manifest['archive_sha256'], 'Archive digest mismatch'
    required = {'index.html', 'fullscore/index.html', 'fullscore/vocalise/index.html',
                'THIRD_PARTY_NOTICES.md', 'fullscore/data/suite5/ATTRIBUTION.txt',
                'fullscore/vendor/browser-bundle/licenses/Gonville-LICENCE.txt'}
    import io
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        infos = z.infolist()
        names = [i.filename for i in infos]
        assert len(names) == len(set(names)), 'Duplicate ZIP entry'
        assert len(infos) <= 2000 and sum(i.file_size for i in infos) <= 250_000_000, 'Archive size limit exceeded'
        files = {}
        for i in infos:
            p = PurePosixPath(i.filename)
            assert i.filename and not p.is_absolute() and '..' not in p.parts, 'Unsafe ZIP path'
            assert '\\' not in i.filename and ':' not in i.filename and not any(ord(c) < 32 for c in i.filename), 'Unsafe ZIP path'
            assert i.filename.rstrip('/') == str(p) and (i.filename == '.nojekyll' or not any(x.startswith('.') for x in p.parts)), 'Noncanonical or hidden ZIP path'
            mode = i.external_attr >> 16
            assert stat.S_IFMT(mode) in (0, stat.S_IFREG, stat.S_IFDIR), 'Special file prohibited'
            assert not i.flag_bits & 1, 'Encrypted ZIP prohibited'
            if i.is_dir():
                continue
            data = z.read(i)
            files[i.filename] = hashlib.sha256(data).hexdigest()
            if i.filename.endswith('.json'):
                json.loads(data)
        assert files == manifest['files'], 'File inventory/digest mismatch'
        assert required <= files.keys(), 'Required entry or attribution missing'
        assert len(files) == manifest['file_count'], 'File count mismatch'
        for name in required:
            assert z.getinfo(name).file_size > 0, 'Empty required file'
    print(f'PASS: {len(files)} files; exact archive/file hashes; safe ZIP paths; required entrypoints and attribution')

if __name__ == '__main__':
    root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    validate((root/'site.zip').read_bytes(), json.loads((root/'release.json').read_text()),
             [p.name for p in root.glob('site*.zip')])
