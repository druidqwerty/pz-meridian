"""Package a tested candidate with source notices, not test drivers/game files."""
from pathlib import Path
import hashlib,json,zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    audit=json.loads((ROOT/'build/static-audit.json').read_text())
    assert not audit['unknown_sprites'] and audit['safe_zero_density_cells']==16
    dist=ROOT/'dist';dist.mkdir(exist_ok=True)
    target=dist/'MeridianLongWayHome-0.1.0-alpha.1.zip'
    source=ROOT/'mod'
    files=[p for p in source.rglob('*') if p.is_file()]
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(files):z.write(p,'MeridianLongWayHome/'+p.relative_to(source).as_posix())
        for name in ('README.md','LICENSE','ATTRIBUTION.md','RELEASE_NOTES.md'):
            z.write(ROOT/name,'MeridianLongWayHome/'+name)
        z.write(ROOT/'tools/CODEC-LICENSE.txt','MeridianLongWayHome/CODEC-LICENSE.txt')
        z.write(ROOT/'tools/CODEC-LICENSE.txt','MeridianLongWayHome/tools/CODEC-LICENSE.txt')
        for p in sorted((ROOT/'docs').rglob('*')):
            if p.is_file():z.write(p,'MeridianLongWayHome/docs/'+p.relative_to(ROOT/'docs').as_posix())
        z.write(ROOT/'RUNTIME.md','MeridianLongWayHome/RUNTIME.md')
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        names=z.namelist()
        assert not any('PrivateOracle' in n or n.endswith(('.jar','.class')) for n in names)
        assert len([n for n in names if n.endswith('.lotheader')])==audit['native_pairs']
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    checksum=dist/'SHA256SUMS.txt';checksum.write_text(digest+'  '+target.name+'\n')
    print(json.dumps(dict(zip=str(target),bytes=target.stat().st_size,sha256=digest),indent=2))


if __name__=='__main__':main()
