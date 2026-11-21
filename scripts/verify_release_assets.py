#!/usr/bin/env python3
"""Check whether a release is absent or already contains the verified assets."""
from hashlib import sha256
import json
from pathlib import Path
import sys


def verify(releases, tag, files):
    matches = [r for page in releases for r in page if r['tag_name'] == tag]
    if not matches:
        return 'absent'
    if len(matches) != 1 or matches[0]['draft']:
        raise ValueError('Expected one published release for the tag')
    assets = matches[0]['assets']
    for path in files:
        matching = [asset for asset in assets if asset['name'] == path.name]
        if len(matching) != 1:
            raise ValueError(f'Expected exactly one release asset: {path.name}')
        if matching[0].get('state') != 'uploaded' or matching[0].get('digest') != 'sha256:' + sha256(path.read_bytes()).hexdigest():
            raise ValueError(f'Published asset is incomplete or differs: {path.name}')
    return 'match'


if __name__ == '__main__':
    try:
        print(verify(json.loads(Path(sys.argv[1]).read_text()), sys.argv[2], [Path(p) for p in sys.argv[3:]]))
    except (ValueError, OSError, KeyError) as error:
        sys.exit(str(error))
