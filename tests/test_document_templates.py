import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('templates',Path(__file__).resolve().parents[1]/'scripts/render_document_template.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class TemplateValidation(unittest.TestCase):
    def setUp(self):
        self.template={'id':'fixture','fields':{k:{'type':'text','required':True} for k in ['title','document_date','author','body']},'sections':[{'title':'事实','field':'body'}],'table':{'title':'行动','headers':['事项','负责人'],'field':'actions'}}
        self.template['fields']['actions']={'type':'rows','required':True}
        self.template['fields']['body']['label']='工作内容'
        self.values={'title':'周报','document_date':'2026-10-17','author':'甲','body':'已完成一项','actions':[['复核','乙']]}
    def test_whitespace_required_field_is_missing(self):
        self.values['body']='   '
        with self.assertRaisesRegex(ValueError,'缺少必填'):m.compile_template(self.template,self.values)
    def test_incomplete_draft_lists_missing_data(self):
        del self.values['body']
        result=m.compile_template(self.template,self.values,True)
        self.assertEqual(result['missingFields'],['body'])
        self.assertIn('工作内容',str(result['steps']))
        self.assertIn('待确认',str(result['steps']))
    def test_unknown_keys_rejected(self):
        self.values['invoice']='wrong template'
        with self.assertRaisesRegex(ValueError,'未知字段'):m.compile_template(self.template,self.values)
    def test_wrong_table_shape_rejected(self):
        self.values['actions']=[['未提供负责人']]
        with self.assertRaisesRegex(ValueError,'行列数'):m.compile_template(self.template,self.values)
    def test_table_delimiters_rejected(self):
        self.values['actions']=[['事项\t伪造另一列','乙']]
        with self.assertRaisesRegex(ValueError,'单元格'):m.compile_template(self.template,self.values)
    def test_heading_body_and_table_selection(self):
        self.values['body']='正文含"引号"和\n换行'
        result=m.compile_template(self.template,self.values)
        steps=result['steps'];self.assertEqual(result['state'],'READY_FOR_REVIEW')
        self.assertNotIn('select.all',[s['command'] for s in steps])
        selected=next(s['params']['text'] for s in steps if s['command']=='select.text')
        self.assertEqual(selected,'事项\t负责人\n复核\t乙')
        rows=[s['params']['text'] for s in steps if s['command']=='text.insert' and '\t' in s['params']['text']]
        self.assertEqual(rows,['事项\t负责人','复核\t乙'])
        pos=next(i for i,s in enumerate(steps) if s['params'].get('text')==self.values['body'])
        self.assertEqual(steps[pos-2]['command'],'para.normal')


class SixDocumentTemplates(unittest.TestCase):
    def test_every_example_compiles_and_copies_are_self_contained(self):
        import hashlib
        import json
        root=Path(__file__).resolve().parents[1]
        records=json.loads((root/'document-templates.json').read_text())['templates']
        self.assertEqual(len(records),6)
        canonical=(root/'scripts/render_document_template.py').read_bytes()
        for record in records:
            folder=root/'skills'/record['skill']
            with self.subTest(skill=record['skill']):
                template=json.loads((folder/'assets/template.json').read_text())
                values=json.loads((folder/'examples/input.json').read_text())
                result=m.compile_template(template,values)
                self.assertEqual(result['missingFields'],[])
                self.assertEqual((folder/'scripts/render_document_template.py').read_bytes(),canonical)
                self.assertEqual(hashlib.sha256((folder/'SKILL.md').read_bytes()).hexdigest(),record['sha256'])
                evidence=json.loads((folder/'references/template-command-evidence.json').read_text())['observedCommands']
                self.assertTrue(all(step['command'] in evidence for step in result['steps']))
    def test_existing_output_prevents_cli_execution(self):
        import json
        import subprocess
        import sys
        import tempfile
        root=Path(__file__).resolve().parents[1]
        folder=root/'skills/wordcraft-weekly-report'
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'steps.json';doc=Path(temp)/'already.docx';doc.write_bytes(b'user data')
            run=subprocess.run([sys.executable,str(folder/'scripts/render_document_template.py'),'--input',str(folder/'examples/input.json'),'--output',str(output),'--save',str(doc),'--cli','nonexistent-cli'],capture_output=True,text=True)
            self.assertEqual(run.returncode,2)
            self.assertFalse(output.exists())
            self.assertEqual(doc.read_bytes(),b'user data')

if __name__=='__main__':unittest.main()
