"""Install only Meridian in the user's cachedir; no save/profile edits."""
from pathlib import Path
from datetime import datetime
import json,shutil

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
    assert all((target/p.relative_to(source)).stat().st_size==p.stat().st_size for p in files)
    receipt=dict(path=str(target),files=len(files),backup=str(backup) if backup else None,
                 profile_changed=False,saves_changed=False)
    (ROOT/'build/install.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
