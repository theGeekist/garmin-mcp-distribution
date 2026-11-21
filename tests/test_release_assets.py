from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from scripts.verify_release_assets import verify

class ReleaseAssets(unittest.TestCase):
    def test_absent_and_complete_releases(self):
        with TemporaryDirectory() as d:
            files=[Path(d)/'one.zip',Path(d)/'SHA256SUMS']
            for p in files:p.write_text(p.name)
            self.assertEqual(verify([[]],'v1',files),'absent')
            assets=[{'name':p.name,'state':'uploaded','digest':'sha256:'+sha256(p.read_bytes()).hexdigest()} for p in files]
            release={'tag_name':'v1','draft':False,'assets':assets}
            self.assertEqual(verify([[release]],'v1',files),'match')
            for altered in (assets[:1], [dict(a,digest='sha256:bad') for a in assets], [dict(a,state='starter') for a in assets]):
                with self.assertRaises(ValueError):verify([[dict(release,assets=altered)]],'v1',files)
            with self.assertRaises(ValueError):verify([[dict(release,draft=True)]],'v1',files)
            with self.assertRaises(ValueError):verify([[release,release]],'v1',files)
