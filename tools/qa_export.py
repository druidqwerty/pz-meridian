"""Export private oracle evidence without local account paths or command lines."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT=Path(__file__).resolve().parents[1]


def clean(value):
    if isinstance(value, dict):
        return {key:clean(item) for key,item in value.items()}
    if isinstance(value, list):
        return [clean(item) for item in value]
    if isinstance(value, str):
        from game_smoke import DEFAULT_GAME
        return value.replace('\\','/').replace(ROOT.as_posix(),'<PROJECT>').replace(
            DEFAULT_GAME.as_posix(),'<GAME>').replace(Path.home().as_posix(),'<USERHOME>')
    return value


def export(run, output, prefix, copy_images):
    from playtest import classify_resource_errors, tree_binding
    meta=json.loads((run/'run.json').read_text(encoding='utf-8'))
    cache=Path(meta['cache'])
    console=(cache/'console.txt').read_text(encoding='utf-8',errors='replace')
    report=cache/'Lua/meridian-playtest.txt'
    records=report.read_text(encoding='utf-8') if report.exists() else '\n'.join(
        line.split('[MeridianTest] ',1)[1] for line in console.splitlines() if '[MeridianTest] ' in line)+'\n'
    output.mkdir(parents=True,exist_ok=True)
    report_name=prefix+('-report.txt' if report.exists() else '-partial-records.txt')
    (output/report_name).write_text(clean(records),encoding='utf-8')
    resource_errors,stock_warnings=classify_resource_errors(console)
    lua_errors=[line for line in console.splitlines() if 'dumping Lua stack trace' in line or 'ERROR: Lua' in line]
    lines=console.splitlines();error_context=[]
    for i,line in enumerate(lines):
        if 'attempted index:' in line or 'dumping Lua stack trace' in line:
            error_context.extend(lines[max(0,i-1):i+7])
            if len(error_context)>=60:
                break
    receipt=dict(run=run.name,wrapperStatus=meta['status'],nativeReportProduced=report.exists(),
        nativeResult=re.findall(r'(?m)^result=(.+)$',records),
        config={key:meta['config'].get(key) for key in ('folder','x','y','z','targets','resume','token')},
        boundSpriteNames=len(meta['config'].get('spriteNames',[])),
        mapResourceErrors=resource_errors,knownStockStartupWarnings=stock_warnings,
        luaErrorLines=lua_errors,luaErrorContext=error_context[:60])
    bind=run/'candidate-bind.json'
    if bind.exists():
        original=json.loads(bind.read_text(encoding='utf-8'))
        receipt['candidateBinding']={key:original[key] for key in ('files','treeSHA256','equal')}
        receipt['candidateBinding'].update(source='mod',copy='isolated oracle cache copy')
    else:
        source=tree_binding(ROOT/'mod')
        isolated=tree_binding(cache/'mods/MeridianLongWayHome')
        receipt['candidateBinding']=dict(files=len(source),equal=source==isolated,
            treeSHA256=hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest(),
            source='mod',copy='isolated reload cache copy')
    (output/(prefix+'-receipt.json')).write_text(json.dumps(clean(receipt),indent=2),encoding='utf-8')
    labels=['world_selection','spawn_selection']+re.findall(r'(?m)^screenshot=(.+)$',records)
    if meta['config'].get('resume'):
        labels=re.findall(r'(?m)^screenshot=(.+)$',records)
    shots=sorted((cache/'Screenshots').glob('*.png'),key=lambda p:p.stat().st_mtime_ns)
    if len(labels)!=len(shots):
        raise ValueError(f'Cannot invent screenshot mapping: {len(labels)} labels, {len(shots)} files')
    index=[]
    for label,file in zip(labels,shots):
        slug=re.sub(r'[^a-z0-9]+','-',label.lower()).strip('-')
        target=prefix+'-'+slug+'.png'
        if copy_images:
            shutil.copy2(file,output/target)
        index.append(dict(label=label,file=target if copy_images else None,original=file.name))
    (output/(prefix+'-screenshot-index.json')).write_text(json.dumps(index,indent=2),encoding='utf-8')
    print(f'Exported {run.name}: {len(index)} screenshot labels; native report={report.exists()}')
    return receipt


if __name__=='__main__':
    import sys
    sys.path.insert(0,str(ROOT.parent/'pz-map-tools/tools'))
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path)
    parser.add_argument('--output',type=Path,default=ROOT/'docs/test-results/2026-11-06-urban')
    parser.add_argument('--prefix',required=True)
    parser.add_argument('--images',action='store_true')
    args=parser.parse_args()
    export(args.run,args.output,args.prefix,args.images)
