"""Fetch the original public UCI CSV and verify its expected SHA-256."""
from pathlib import Path
from urllib.request import urlopen
import io,json,hashlib,zipfile
root=Path(__file__).resolve().parent
cfg=json.loads((root/'source.json').read_text())
with urlopen(cfg['url'],timeout=60) as response:
    raw=response.read()
with zipfile.ZipFile(io.BytesIO(raw)) as archive:
    if cfg['nested']:
        with zipfile.ZipFile(io.BytesIO(archive.read(cfg['nested']))) as inner:
            csv=inner.read(cfg['member'])
    else:
        csv=archive.read(cfg['member'])
actual=hashlib.sha256(csv).hexdigest()
if actual!=cfg['sha256']:
    raise ValueError('Source checksum changed. Review the upstream file before updating source.json.')
(root/'data').mkdir(exist_ok=True)
(root/'data'/cfg['target']).write_bytes(csv)
print('Verified:',cfg['target'],actual)
