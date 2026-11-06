"""Install only Meridian in the user's cachedir; no save/profile edits."""
from pathlib import Path
from datetime import datetime
import hashlib,json,shutil

ROOT=Path(__file__).resolve().parents[1]


def main():
    source=ROOT/'mod';target=Path.home()/'Zomboid/mods/MeridianLongWayHome'
    assert (source/'42/mod.info').is_file()
    assert 'id=MeridianLongWayHome' in (source/'42/mod.info').read_text()
    assert target.resolve().parent==(Path.home()/'Zomboid/mods').resolve()
    backup=None
    if target.exists():
        backup=ROOT/'build/install-backups'/datetime.now().strftime('%Y%m%d-%H%M%S')
        backup.parent.mkdir(parents=True,exist_ok=True)
        shutil.move(str(target),str(backup))
    shutil.copytree(source,target)
    files=[p for p in source.rglob('*') if p.is_file()]
    def digest(path):
        h=hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
        return h.hexdigest()
    hashes={}
    for p in files:
        rel=p.relative_to(source)
        hashes[rel.as_posix()]=digest(p)
        assert digest(target/rel)==hashes[rel.as_posix()],f'Copy changed {rel}'
    (ROOT/'build/install-files.json').write_text(json.dumps(hashes,indent=2))
    receipt=dict(path=str(target),files=len(files),backup=str(backup) if backup else None,
                 profile_changed=False,saves_changed=False,sha256_verified=True)
    (ROOT/'build/install.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
