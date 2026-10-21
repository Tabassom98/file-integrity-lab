"""Create and compare SHA-256 manifests for a local directory."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def snapshot(root):
    root=Path(root)
    if root.is_symlink() or (hasattr(root,'is_junction') and root.is_junction()) or not root.is_dir():
        raise ValueError('root must be an existing directory without a link or junction')
    result={}
    for path in sorted(root.rglob('*')):
        if path.is_symlink() or (hasattr(path,'is_junction') and path.is_junction()):
            raise ValueError('links and junctions are not supported')
        if path.is_file():
            digest=hashlib.sha256()
            with path.open('rb') as stream:
                for block in iter(lambda:stream.read(65536),b''): digest.update(block)
            result[path.relative_to(root).as_posix()]=digest.hexdigest()
        elif not path.is_dir(): raise ValueError('special files are not supported')
    return result


def validate(manifest):
    if not isinstance(manifest,dict): raise ValueError('manifest must be an object')
    for name,digest in manifest.items():
        if not isinstance(name,str) or not name or name.startswith('/') or '\\' in name or ':' in name or any(p in ('','..','.') for p in name.split('/')):
            raise ValueError('invalid manifest path')
        if not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('invalid SHA-256 digest')
    return manifest


def compare(before,after):
    validate(before)
    validate(after)
    return dict(added=sorted(after.keys()-before.keys()),removed=sorted(before.keys()-after.keys()),
                modified=sorted(k for k in before.keys() & after.keys() if before[k]!=after[k]))


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['baseline','check'])
    parser.add_argument('directory',type=Path)
    parser.add_argument('manifest',type=Path)
    args=parser.parse_args(argv)
    try:
        root=args.directory.resolve()
        manifest=args.manifest.resolve()
        if manifest==root or root in manifest.parents: raise ValueError('store the manifest outside the monitored directory')
        current=snapshot(args.directory)
        if args.command=='baseline':
            with args.manifest.open('x',encoding='utf-8') as stream: json.dump(current,stream,indent=2,sort_keys=True)
            print(json.dumps(dict(files=len(current),status='baseline created')))
            return 0
        before=validate(json.loads(args.manifest.read_text(encoding='utf-8')))
        result=compare(before,current)
        print(json.dumps(result,indent=2,sort_keys=True))
        return 1 if any(result.values()) else 0
    except (ValueError,OSError) as exc:
        print(f'error: {exc}',file=sys.stderr)
        return 2


if __name__=='__main__': raise SystemExit(main())
