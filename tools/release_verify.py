"""Bind a release ZIP and installed copy to the exact successfully tested bytes."""
from pathlib import Path
import argparse,hashlib,json,zipfile
from version import VERSION

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',type=Path,required=True)
    p.add_argument('--zip',type=Path)
    args=p.parse_args()
    meta=json.loads((args.run/'run.json').read_text(encoding='utf-8'))
    assert meta['status']=='passed',meta['status']
    binding=json.loads((args.run/'candidate-bind.json').read_text(encoding='utf-8'))
    assert binding['equal'], 'Test launch source/copy binding did not match'
    entries=binding['entries']
    install=json.loads((ROOT/'build/install-files.json').read_text())
    installed=Path(json.loads((ROOT/'build/install.json').read_text())['path'])
    tested=Path(meta['cache'])/'mods/MeridianLongWayHome'
    current={f.relative_to(ROOT/'mod').as_posix():f for f in (ROOT/'mod').rglob('*') if f.is_file()}
    assert set(current)==set(entries)==set(install)
    for folder in (installed,tested):
        assert {f.relative_to(folder).as_posix() for f in folder.rglob('*') if f.is_file()}==set(entries),folder
    for name,path in current.items():
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest==entries[name]['sha256']==install[name],name
        assert path.stat().st_size==entries[name]['bytes'],name
        assert hashlib.sha256((installed/name).read_bytes()).hexdigest()==digest,('installed',name)
        assert hashlib.sha256((tested/name).read_bytes()).hexdigest()==digest,('tested',name)
    receipt=dict(version=VERSION,files=len(entries),candidateTreeSHA256=binding['treeSHA256'],
        sameAsSuccessfulGameRun=True,sameAsInstalledCopy=True)
    if args.zip:
        with zipfile.ZipFile(args.zip) as archive:
            assert archive.testzip() is None
            for name in entries:
                data=archive.read('MeridianLongWayHome/'+name)
                assert hashlib.sha256(data).hexdigest()==entries[name]['sha256'],name
        receipt.update(zip=args.zip.name,bytes=args.zip.stat().st_size,
            sha256=hashlib.sha256(args.zip.read_bytes()).hexdigest(),sameAsReleaseZip=True)
    (ROOT/'build/urban-release-verification.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
