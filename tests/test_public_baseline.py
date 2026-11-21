import hashlib
from io import BytesIO
import json
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch
from scripts import distribution
import unittest
from zipfile import ZipFile
from scripts.sync_public_baseline import FILES, sync

class PublicBaseline(unittest.TestCase):
    def baseline(self, folder, *, extra=False, owner=False):
        meta={'id':'garmin-mcp','version':'1.2.3','description':'Public description',
              'displayName':'Garmin','shortDescription':'Garmin data','publisher':'Geekist',
              'publisherWebsite':'https://geekist.co','dataProvider':'Garmin','category':'Data & Analytics',
              'candidatePrompts':['Explore'],'mcpEndpoint':'https://garmin.geekist.co/mcp',
              'whatsappURL':'https://wa.me/message/NYYMWFMR5FM2L1','supportEmail':'garmin@geekist.co'}
        urls={key:'https://garmin.geekist.co/' for key in ('websiteURL','supportURL','privacyPolicyURL','termsOfServiceURL')}
        meta.update(urls)
        review={'review':{},'publication':{'release_notes':'Public release notes.'}}
        body={name:b'public content' for name in FILES}
        body.update({'distribution.json':json.dumps(meta).encode(),'openai-review.json':json.dumps(review).encode()})
        if extra: body['private/notes.md']=b'private'
        if owner: body[FILES[0]]=b'Use owner_read_inbox'
        out=BytesIO()
        with ZipFile(out,'w') as z:
            for path,data in body.items():z.writestr(path,data)
        file=folder/'baseline.zip';file.write_bytes(out.getvalue())
        return file,hashlib.sha256(out.getvalue()).hexdigest()

    def target(self, folder):
        dest=folder/'dest';(dest/'catalogue').mkdir(parents=True);(dest/'docs/clients').mkdir(parents=True)
        original={'release':{'productionMcp':{'url':'https://garmin.geekist.co/mcp','verification':'preserved'},'openaiReview':'preserved'}}
        (dest/'catalogue/garmin.json').write_text(json.dumps(original))
        (dest/'server.json').write_text(json.dumps({'name':'io.github.theGeekist/garmin-mcp','version':'0.3.6','remotes':[{'url':'https://garmin.geekist.co/mcp'}]}))
        (dest/'CHANGELOG.md').write_text('# Changes\n\n## 0.3.6\n\n- Earlier change.\n')
        (dest/'README.md').write_text('garmin-mcp-0.3.6-openai.zip')
        (dest/'docs/clients/README.md').write_text('garmin-mcp-0.3.6-claude-code.zip')
        return dest

    def test_imports_only_public_inputs_and_preserves_release_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);archive,digest=self.baseline(base);dest=self.target(base)
            sync(archive,digest,dest)
            catalog=json.loads((dest/'catalogue/garmin.json').read_text())
            self.assertEqual(catalog['version'],'1.2.3')
            self.assertEqual(json.loads((dest/'server.json').read_text())['version'],'1.2.3')
            self.assertEqual(catalog['release']['openaiReview'],'preserved')
            self.assertIn('## 1.2.3\n\n- Public release notes.',(dest/'CHANGELOG.md').read_text())
            self.assertIn('garmin-mcp-1.2.3-openai.zip',(dest/'README.md').read_text())
            self.assertEqual((dest/'upstream/baseline-sha256.txt').read_text().strip(),digest)
            self.assertFalse((dest/'LICENSE').exists())
            self.assertFalse((dest/'assets').exists())

    def test_imported_inputs_reach_each_provider_without_replacing_branding(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);archive,digest=self.baseline(base);dest=self.target(base)
            root=Path(__file__).resolve().parents[1]
            shutil.copytree(root/'assets',dest/'assets')
            shutil.copy(root/'LICENSE',dest/'LICENSE')
            sync(archive,digest,dest)
            with patch.object(distribution,'ROOT',dest):
                files=distribution.output_files(distribution.inputs())
            for name in ('openai/garmin-mcp/skills/garmin-review/SKILL.md',
                         'claude/plugins/garmin-mcp/skills/garmin-review/SKILL.md',
                         'gemini/garmin-mcp/skills/garmin-review/SKILL.md'):
                self.assertEqual(files[Path(name)],b'public content')
            manifest=json.loads(files[Path('openai/garmin-mcp/plugin.json')])
            self.assertEqual(manifest['version'],'1.2.3')
            self.assertEqual(files[Path('gemini/garmin-mcp/GEMINI.md')],b'public content')
            self.assertEqual(files[Path('openai/garmin-mcp/LICENSE')],(root/'LICENSE').read_bytes())
            self.assertEqual(files[Path('openai/garmin-mcp/assets/garmin-mcp-product-logo.png')],(root/'assets/garmin-mcp-product-logo.png').read_bytes())
            self.assertEqual(len([p for p in files if p.suffix=='.zip']),6)

    def test_rejects_downgrade_and_registry_mismatch_without_writes(self):
        for mode in ('downgrade','registry'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                base=Path(tmp);archive,digest=self.baseline(base);dest=self.target(base)
                if mode == 'downgrade':
                    p=dest/'catalogue/garmin.json';data=json.loads(p.read_text());data['version']='9.0.0';p.write_text(json.dumps(data))
                else:
                    p=dest/'server.json';data=json.loads(p.read_text());data['name']='other';p.write_text(json.dumps(data))
                before=(dest/'catalogue/garmin.json').read_bytes()
                with self.assertRaises(ValueError):sync(archive,digest,dest)
                self.assertEqual((dest/'catalogue/garmin.json').read_bytes(),before)

    def test_rejects_wrong_digest_extra_files_and_owner_guidance(self):
        for opts in ({'extra':True},{'owner':True},{}):
            with self.subTest(opts=opts), tempfile.TemporaryDirectory() as tmp:
                base=Path(tmp);archive,digest=self.baseline(base,**opts);dest=self.target(base)
                before=(dest/'catalogue/garmin.json').read_bytes()
                with self.assertRaises(ValueError):sync(archive,digest if opts else '0'*64,dest)
                self.assertEqual((dest/'catalogue/garmin.json').read_bytes(),before)
