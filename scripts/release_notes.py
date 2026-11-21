#!/usr/bin/env python3
"""Extract the public changelog entry for an exact distribution version."""
from pathlib import Path
import re
import sys


def release_notes(text, version):
    if not re.fullmatch(r'(?:0|[1-9]\d*)(?:\.(?:0|[1-9]\d*)){2}', version):
        raise ValueError('Invalid release version')
    sections = list(re.finditer(r'^## (\d+\.\d+\.\d+)\s*$', text, re.M))
    matches = [i for i, match in enumerate(sections) if match.group(1) == version]
    if len(matches) != 1:
        raise ValueError('Expected exactly one public changelog entry for this version')
    index = matches[0]
    start = sections[index].end()
    end = sections[index + 1].start() if index + 1 < len(sections) else len(text)
    result = text[start:end].strip()
    if not result:
        raise ValueError('Public changelog entry is empty')
    return result + '\n'


if __name__ == '__main__':
    try:
        print(release_notes(Path(sys.argv[1]).read_text(), sys.argv[2]), end='')
    except (ValueError, OSError) as error:
        sys.exit(str(error))
