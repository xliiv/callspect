import io
import os
import unittest

# MUST BE before app import
from callspect import config
config.config_dict = {
    'TESTING': '1'
}

import callspect


class MergerToSeqDiagTest(unittest.TestCase):
    def setUp(self):
        self.merger = callspect.MergerToSeqDiag()

    def test_no_call_works(self):
        filelike = io.StringIO('\n'.join([
        ]))

        self.merger.parse(filelike)

        self.assertEqual(self.merger.merged(), 'participant MainThread')

    def test_single_call_works(self):
        filelike = io.StringIO('\n'.join([
            #TODO: return values and call_args should be checked with dedictad testcase
            '{"event": "call", "entity_path": "m1.a", "call_args": {}}',
            '{"event": "return", "entity_path": "m1.a", "return_value": null}',
        ]))

        self.merger.parse(filelike)

        expected = '\n'.join([
            "MainThread->m1.a: {}",
            "m1.a-->MainThread: None",
        ])
        self.assertEqual(self.merger.merged(), expected)

    def test_double_call_works(self):
        filelike = io.StringIO('\n'.join([
            '{"event": "call", "entity_path": "m1.a", "call_args": {}}',
            '{"event": "call", "entity_path": "m1.a_b", "call_args": {}}',
            '{"event": "return", "entity_path": "m1.a_b", "return_value": null}',
            '{"event": "return", "entity_path": "m1.a", "return_value": null}',
        ]))

        self.merger.parse(filelike)

        expected = '\n'.join([
            "MainThread->m1.a: {}",
            "m1.a->m1.a_b: {}",
            "m1.a_b-->m1.a: None",
            "m1.a-->MainThread: None",
        ])
        self.assertEqual(self.merger.merged(), expected)

    def test_filtering_actor_works(self):
        filelike = io.StringIO('\n'.join([
            '{"event": "call", "entity_path": "m1.1", "call_args": {}}',
            '{"event": "call", "entity_path": "m1.1_2", "call_args": {}}',
            '{"event": "call", "entity_path": "m1.1_2_3", "call_args": {}}',
            '{"event": "call", "entity_path": "m1.1_2_3_4", "call_args": {}}',
            '{"event": "call", "entity_path": "m1.1_2_3_4_5", "call_args": {}}',
            '{"event": "return", "entity_path": "m1.1_2_3_4_5", "return_value": null}',
            '{"event": "return", "entity_path": "m1.1_2_3_4", "return_value": null}',
            '{"event": "return", "entity_path": "m1.1_2_3", "return_value": null}',
            '{"event": "return", "entity_path": "m1.1_2", "return_value": null}',
            '{"event": "return", "entity_path": "m1.1", "return_value": null}',
        ]))

        self.merger.parse(filelike)
        self.merger.single_actor('m1.1_2_3')

        expected_list = [
            "m1.1_2->m1.1_2_3",
            "m1.1_2_3->m1.1_2_3_4",
            "m1.1_2_3_4-->m1.1_2_3",
            "m1.1_2_3-->m1.1_2",
        ]
        for line, expected in zip(self.merger.merged().split('\n'), expected_list):
            line_beginning = line.split(':')[0]
            self.assertEqual(line_beginning, expected)


class MergerToCallTreeTest(unittest.TestCase):
    def setUp(self):
        self.merger = callspect.MergerToCallTree()

    def test_no_call_works(self):
        filelike = io.StringIO('\n'.join([
        ]))

        self.merger.parse(filelike)

        self.assertEqual(
            self.merger.merged(),
            [{
                'label': 'MainThread', 'children': []
            }]
        )

    def test_single_depth_works(self):
        filelike = io.StringIO('\n'.join([
            '{"event": "call", "entity_path": "m1.a"}',
            '{"event": "return", "entity_path": "m1.a"}',
        ]))

        self.merger.parse(filelike)

        self.assertEqual(
            self.merger.merged(),
            [{
            'label': 'MainThread',
            'children': [{'label': 'm1.a', 'children': []}]
            }]
        )

    def test_double_length_works(self):
        filelike = io.StringIO('\n'.join([
            '{"event": "call", "entity_path": "m1.a"}',
            '{"event": "call", "entity_path": "m1.b"}',
            '{"event": "return", "entity_path": "m1.b"}',
            '{"event": "return", "entity_path": "m1.a"}',
        ]))

        self.merger.parse(filelike)

        expected = [{
            'label': 'MainThread',
            'children': [{
                'label': 'm1.a',
                'children': [{
                    'label': 'm1.b',
                    'children': []
                }]
            }]
        }]
        self.assertEqual(self.merger.merged(), expected)

    def test_single_and_double_depth_length_works(self):
        filelike = io.StringIO('\n'.join([
            '{"event": "call", "entity_path": "m1.a"}',
            '{"event": "call", "entity_path": "m1.a_b"}',
            '{"event": "return", "entity_path": "m1.a_b"}',
            '{"event": "return", "entity_path": "m1.a"}',
            '{"event": "call", "entity_path": "m1.b"}',
            '{"event": "return", "entity_path": "m1.b"}',
        ]))

        self.merger.parse(filelike)

        expected = [{
            'label': 'MainThread',
            'children': [{
                'label': 'm1.a',
                'children': [{'label': 'm1.a_b', 'children': []}],
            }, {
                'label': 'm1.b',
                'children': [],
            }]
        }]
        self.assertEqual(self.merger.merged(), expected)


if __name__ == "__main__":
    unittest.main()
