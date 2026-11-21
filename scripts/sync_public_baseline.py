#!/usr/bin/env python3
"""Import the seven reviewed public baseline files for provider packaging."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    'skills/garmin-review/SKILL.md',
    'skills/garmin-review/references/reading.md',
    'skills/garmin-review/references/changes.md',
    'skills/garmin-review/references/service-messages.md',
    'providers/gemini/GEMINI.md',
)
EXPECTED = frozenset((*FILES, 'distribution.json', 'openai-review.json'))
KEYS = frozenset(('id', 'version', 'description', 'displayName', 'shortDescription',
                  'publisher', 'publisherWebsite', 'dataProvider', 'category', 'candidatePrompts', 'mcpEndpoint',
                  'websiteURL', 'supportURL', 'whatsappURL', 'supportEmail', 'privacyPolicyURL', 'termsOfServiceURL'))
URL_KEYS = ('websiteURL', 'supportURL', 'privacyPolicyURL', 'termsOfServiceURL')


def sync(archive, digest, target=ROOT):
    if not re.fullmatch(r'[0-9a-f]{64}', digest):
        raise ValueError('A lowercase SHA-256 digest is required')
    if sha256(archive.read_bytes()).hexdigest() != digest:
        raise ValueError('Baseline digest mismatch')
    with ZipFile(archive) as z:
        names = z.namelist()
        if len(names) != len(EXPECTED) or set(names) != EXPECTED:
            raise ValueError('Baseline must contain exactly the seven public inputs')
        if any(info.file_size > 128 * 1024 for info in z.infolist()):
            raise ValueError('Baseline member exceeds size limit')
        payload = {name: z.read(name) for name in EXPECTED}
    for name, content in payload.items():
        if re.search(rb'owner_|ownerNotices|owner inbox|owner workflows|owner-notice', content, re.I):
            raise ValueError(f'Private owner guidance in {name}')
    metadata = json.loads(payload['distribution.json'])
    review = json.loads(payload['openai-review.json'])
    if set(metadata) != KEYS or metadata['id'] != 'garmin-mcp' or not re.fullmatch(r'(?:0|[1-9]\d*)(?:\.(?:0|[1-9]\d*)){2}',metadata['version']):
        raise ValueError('Invalid public package identity or metadata')
    if metadata['mcpEndpoint'] != 'https://garmin.geekist.co/mcp':
        raise ValueError('Unexpected public MCP endpoint')
    if set(review) != {'review', 'publication'}:
        raise ValueError('Unexpected OpenAI review metadata')
    catalog_path = target / 'catalogue/garmin.json'
    catalog = json.loads(catalog_path.read_text())
    old_version = catalog.get('version', '0.0.0')
    if not re.fullmatch(r'(?:0|[1-9]\d*)(?:\.(?:0|[1-9]\d*)){2}', old_version) or tuple(map(int, metadata['version'].split('.'))) < tuple(map(int, old_version.split('.'))):
        raise ValueError('Baseline must not downgrade the distribution version')
    if catalog['release']['productionMcp']['url'] != metadata['mcpEndpoint']:
        raise ValueError('Public catalogue endpoint differs from baseline')
    registry_path = target / 'server.json'
    registry = json.loads(registry_path.read_text())
    if registry.get('name') != 'io.github.theGeekist/garmin-mcp' or not any(r.get('url') == metadata['mcpEndpoint'] for r in registry.get('remotes', [])):
        raise ValueError('Registry identity or endpoint differs from baseline')
    registry['version'] = metadata['version']
    for key in ('id','version','description','displayName','shortDescription','publisher','publisherWebsite','dataProvider','category','candidatePrompts'):
        catalog[key] = metadata[key]
    changelog_path = target / 'CHANGELOG.md'
    changelog = changelog_path.read_text()
    heading = f"## {metadata['version']}"
    headings = re.findall(r'^## (\d+\.\d+\.\d+)\s*$', changelog, re.M)
    if headings.count(metadata['version']) > 1:
        raise ValueError('Duplicate public changelog version')
    if metadata['version'] not in headings:
        notes = review['publication'].get('release_notes')
        if not isinstance(notes, str) or not notes.strip() or '\n' in notes or len(notes) > 1000:
            raise ValueError('A concise public release note is required')
        first = re.search(r'^## \d+\.\d+\.\d+\s*$', changelog, re.M)
        if not first:
            raise ValueError('Public changelog has no version headings')
        changelog = changelog[:first.start()] + heading + '\n\n- ' + notes.strip() + '\n\n' + changelog[first.start():]
    changelog_path.write_text(changelog)
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n')
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n')
    for name in FILES:
        dest = target / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(payload[name])
    target_file = target / 'upstream/openai-review.json'
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_bytes(payload['openai-review.json'])
    (target / 'upstream/public-urls.json').write_text(json.dumps({k: metadata[k] for k in URL_KEYS}, indent=2) + '\n')
    (target / 'upstream/baseline-sha256.txt').write_text(digest + '\n')
    for name in ('README.md', 'docs/clients/README.md'):
        path = target / name
        path.write_text(re.sub(r'garmin-mcp-\d+\.\d+\.\d+-(?=(?:codex-marketplace|claude-code|claude-plugin|gemini-cli|antigravity|openai)\.zip)',
                               f"garmin-mcp-{metadata['version']}-", path.read_text()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args()
    sync(args.baseline, args.sha256)
