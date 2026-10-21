import hashlib
from pathlib import Path
import tempfile
import unittest
from integrity import snapshot,compare,validate,main

class Tests(unittest.TestCase):
    def test_known_digest(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder)/'a').write_bytes(b'abc')
            self.assertEqual(snapshot(folder),{'a':'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'})
    def test_added_removed_modified(self):
        a=hashlib.sha256(b'a').hexdigest()
        b=hashlib.sha256(b'b').hexdigest()
        self.assertEqual(compare({'old':a,'same':a,'change':a},{'new':b,'same':a,'change':b}),dict(added=['new'],removed=['old'],modified=['change']))
    def test_empty(self):
        self.assertEqual(compare({},{}),dict(added=[],removed=[],modified=[]))
    def test_binary_and_nested_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'nested').mkdir()
            (root/'nested/binary').write_bytes(bytes(range(256))*1000)
            expected=hashlib.sha256(bytes(range(256))*1000).hexdigest()
            self.assertEqual(snapshot(root),{'nested/binary':expected})
    def test_content_not_size(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'a'
            path.write_bytes(b'abc')
            before=snapshot(folder)
            path.write_bytes(b'xyz')
            self.assertEqual(compare(before,snapshot(folder))['modified'],['a'])
    def test_invalid_manifest(self):
        for name in ('../file','/absolute','C:/file','a//b','a/./b','a\\b'):
            with self.subTest(name=name),self.assertRaises(ValueError): validate({name:'0'*64})
        with self.assertRaises(ValueError): validate({'file':'bad'})
    def test_missing_root(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError): snapshot(Path(folder)/'missing')
    def test_cli_no_overwrite_and_change_codes(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'files'
            root.mkdir()
            (root/'a').write_text('before')
            manifest=Path(folder)/'baseline.json'
            self.assertEqual(main(['baseline',str(root),str(manifest)]),0)
            original=manifest.read_bytes()
            self.assertEqual(main(['baseline',str(root),str(manifest)]),2)
            self.assertEqual(manifest.read_bytes(),original)
            self.assertEqual(main(['check',str(root),str(manifest)]),0)
            (root/'a').write_text('after')
            self.assertEqual(main(['check',str(root),str(manifest)]),1)
    def test_manifest_inside_root_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(main(['baseline',folder,str(Path(folder)/'baseline.json')]),2)

if __name__=='__main__': unittest.main()
