import unittest,sys; sys.path.insert(0,'src')
from toolgraph_profiler.core import *
class T(unittest.TestCase):
 def test_critical_path(self):
  r=analyze(parse([{'id':'a','name':'a','start':0,'end':1},{'id':'b','name':'b','start':1,'end':4,'parent':'a'},{'id':'c','name':'c','start':1,'end':2,'parent':'a'}])); self.assertEqual(r['critical_path'],['a','b']); self.assertEqual(r['critical_path_duration'],4)
 def test_retries(self): self.assertEqual(analyze(parse([{'id':'1','name':'x','start':0,'end':1},{'id':'2','name':'x','start':1,'end':2}]))['retry_candidates']['x'],1)
 def test_svg(self): self.assertIn('<rect',svg(parse([{'id':'1','name':'x','start':0,'end':1}])))
