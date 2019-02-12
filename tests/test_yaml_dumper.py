from unittest import TestCase
import yaml
from waddle.param_bunch import YamlDumper


__all__ = [
    'YamlDump',
]


class YamlDump(TestCase):
    def test_dumper(self):
        data = { 'cat': 'Taylor' }
        output = yaml.dump(data, Dumper=YamlDumper, default_flow_style=True)
        self.assertEqual(output, '--- {cat: Taylor}\n')
        output = yaml.dump(data, Dumper=YamlDumper, explicit_start=False)
        self.assertEqual(output, 'cat: Taylor\n')
        data = {
            'cats': [{
                'name': 'Taylor',
            }, {
                'name': 'Sesame'
            }],
        }
        output = yaml.dump(data, Dumper=YamlDumper, indent=2)
        self.assertEqual(
            '---\ncats:\n  - name: Taylor\n  - name: Sesame\n',
            output)
        output = yaml.dump(data, Dumper=YamlDumper, line_break='\r\n')
        self.assertEqual(
            '---\r\ncats:\r\n  - name: Taylor\r\n  - name: Sesame\r\n',
            output)
