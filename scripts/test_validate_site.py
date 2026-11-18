from validate_site import validate
from pathlib import Path
import hashlib, json, zipfile
import io, copy
data=Path('site.zip').read_bytes()
manifest=json.loads(Path('release.json').read_text())
validate(data,manifest,['site.zip'])
def rejected(label,b,m,names=['site.zip']):
    try: validate(b,m,names)
    except (AssertionError, ValueError, zipfile.BadZipFile): print('REJECTED:', label); return
    raise RuntimeError('Guard failed: '+label)
rejected('extra archive',data,manifest,['site.zip','site-old.zip'])
rejected('digest corruption',data+b'x',manifest)
m=copy.deepcopy(manifest);m['files'].pop('index.html');rejected('inventory mismatch',data,m)
def mutate(label,name,body,remove=None):
    out=io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as src, zipfile.ZipFile(out,'w') as dst:
        for i in src.infolist():
            if i.filename!=remove: dst.writestr(i,src.read(i))
        if name: dst.writestr(name,body)
    b=out.getvalue()
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        m=copy.deepcopy(manifest);m['archive_sha256']=hashlib.sha256(b).hexdigest()
        m['files']={i.filename:hashlib.sha256(z.read(i)).hexdigest() for i in z.infolist() if not i.is_dir()}
        m['file_count']=len(m['files'])
    rejected(label,b,m)
mutate('path traversal','../outside.txt',b'bad')
mutate('absolute path','/outside.txt',b'bad')
mutate('duplicate entry','index.html',b'bad')
mutate('missing attribution',None,b'',remove='THIRD_PARTY_NOTICES.md')
mutate('malformed JSON','extra.json',b'{')
print('TESTS PASS: baseline + 8 negative cases')
