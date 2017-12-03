import os
import tempfile
import unittest

import callspectpy


def single_call():
    pass


def double_call():
    single_call()
    single_call()


def a():
    def a_b():
        pass
    a_b()


def a_calls_a_few_other_fn():
    def b():
        pass
    def c():
        pass
    def d():
        pass
    def e():
        pass
    b()
    c()
    d()
    e()


def a_start_chained_call():
    def b():
        c()
    def c():
        d()
    def d():
        e()
    def e():
        pass
    b()


def fn_creates_obj_of_class_A():
    class A:
        def __init__(self):
            pass
    obj = A()

def fn_calls_method_of_obj_of_class_A():
    class A:
        def print(self, txt):
            pass
    obj = A()
    obj.print("txt")

def fn_calls_method_which_calls_module_fn():
    class A:
        def call_module_fn(self):
            single_call()
    obj = A()
    obj.call_module_fn()

def fn_creates_two_objs_of_same_class():
    class A:
        pass
    obj1 = A()
    obj2 = A()


class Collector:
    def __init__(self):
        self.collected = []
    def append(self, data_dict):
        self.collected.append(data_dict)


class DataCollectionTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.collector = Collector()

    def test_event_is_collected(self):
        with callspectpy.trace(self.collector):
            single_call()

        self.assertEqual(self.collector.collected[0]['event'], 'call')
        self.assertEqual(self.collector.collected[1]['event'], 'return')

    def test_absolute_filepath_is_collected(self):
        with callspectpy.trace(self.collector):
            single_call()

        exp = os.path.abspath(__file__)
        self.assertEqual(self.collector.collected[0]['abs_filepath'], exp)
        self.assertEqual(self.collector.collected[1]['abs_filepath'], exp)

    def test_line_number_is_collected(self):
        with callspectpy.trace(self.collector):
            single_call()

        # TODO: mv single_call to exclusive file
        # storing single_call in editable file (like this)
        # breaks this test on each edition
        self.assertEqual(self.collector.collected[0]['line_number'], 8)
        self.assertEqual(self.collector.collected[1]['line_number'], 8)

    def test_module_is_collected(self):
        with callspectpy.trace(self.collector):
            single_call()

        self.assertEqual(self.collector.collected[0]['module'], 'tests')
        self.assertEqual(self.collector.collected[1]['module'], 'tests')

    def test_callspect_calls_are_skipped(self):
        with callspectpy.trace(self.collector):
            pass

        self.assertEqual(self.collector.collected, [])


    @unittest.skip("TODO")
    def test_call_args_are_collected(self):
        #TODO: ensure kwargs are collected too
        pass

    @unittest.skip("TODO")
    def test_returns_value_is_collected(self):
        pass


class FormatterJsonTest(unittest.TestCase):
    def setUp(self):
        self.formatter = callspectpy.FormatterJson()

    def test_obj_is_serialized_as_string(self):
        fp  = tempfile.TemporaryFile()
        data_dict = {
            #'call_args': {'obj': <_io.BufferedRandom name=3>}
            'call_args': {'obj': fp },
        }

        jsonable = self.formatter.make_jsonable(data_dict)

        self.assertEqual(
            jsonable,
            {'call_args': "{'obj': <_io.BufferedRandom name=3>}"}
        )

    def test_data_is_jsoned_if_key_is_tuple(self):
        data_dict = {
            'call_args': { (1,2): '1,2' }
        }

        jsonable = self.formatter.make_jsonable(data_dict)

        print(jsonable)
        self.assertEqual(jsonable, {'call_args': "{(1, 2): '1,2'}"})


class MultipleFnCallsTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.collector = Collector()

    def test_no_call_works(self):
        with callspectpy.trace(self.collector):
            pass

        self.assertEqual(self.collector.collected, [])

    def test_single_call_works(self):
        with callspectpy.trace(self.collector):
            a()

        found = self.collector.collected
        expected = (
            {'event': 'call', 'fn': 'a', 'module': 'tests',},
            {'event': 'call', 'fn': 'a_b', 'module': 'tests',},
            {'event': 'return', 'fn': 'a_b', 'module': 'tests',},
            {'event': 'return', 'fn': 'a', 'module': 'tests',},
        )
        for idx, data_dict in enumerate(expected):
            self.assertEqual(found[idx]['event'], data_dict['event'])
            self.assertEqual(found[idx]['fn'], data_dict['fn'])

    def test_double_call_works(self):
        with callspectpy.trace(self.collector):
            double_call()

        found = self.collector.collected
        expected = (
            {'event': 'call', 'fn': 'double_call', 'module': 'tests',},
            {'event': 'call', 'fn': 'single_call', 'module': 'tests',},
            {'event': 'return', 'fn': 'single_call', 'module': 'tests',},
            {'event': 'call', 'fn': 'single_call', 'module': 'tests',},
            {'event': 'return', 'fn': 'single_call', 'module': 'tests',},
            {'event': 'return', 'fn': 'double_call', 'module': 'tests',},
        )
        for idx, data_dict in enumerate(expected):
            self.assertEqual(found[idx]['event'], data_dict['event'])
            self.assertEqual(found[idx]['fn'], data_dict['fn'])

    def test_a_calls_a_few_other_fn_works(self):
        with callspectpy.trace(self.collector):
            a_calls_a_few_other_fn()

        found = self.collector.collected
        expected = (
            {'event': 'call', 'fn': 'a_calls_a_few_other_fn', 'module': 'tests'},
            {'event': 'call', 'fn': 'b', 'module': 'tests'},
            {'event': 'return', 'fn': 'b', 'module': 'tests'},
            {'event': 'call', 'fn': 'c', 'module': 'tests'},
            {'event': 'return', 'fn': 'c', 'module': 'tests'},
            {'event': 'call', 'fn': 'd', 'module': 'tests'},
            {'event': 'return', 'fn': 'd', 'module': 'tests'},
            {'event': 'call', 'fn': 'e', 'module': 'tests'},
            {'event': 'return', 'fn': 'e', 'module': 'tests'},
            {'event': 'return', 'fn': 'a_calls_a_few_other_fn', 'module': 'tests'},
        )
        for idx, data_dict in enumerate(expected):
            self.assertEqual(found[idx]['event'], data_dict['event'])
            self.assertEqual(found[idx]['fn'], data_dict['fn'])

    def test_a_start_chained_calls_works(self):
        with callspectpy.trace(self.collector):
            a_start_chained_call()

        found = self.collector.collected
        expected = (
            {'event': 'call', 'fn': 'a_start_chained_call',},
            {'event': 'call', 'fn': 'b',},
            {'event': 'call', 'fn': 'c',},
            {'event': 'call', 'fn': 'd',},
            {'event': 'call', 'fn': 'e',},
            {'event': 'return', 'fn': 'e',},
            {'event': 'return', 'fn': 'd',},
            {'event': 'return', 'fn': 'c',},
            {'event': 'return', 'fn': 'b',},
            {'event': 'return', 'fn': 'a_start_chained_call',},
        )
        for idx, data_dict in enumerate(expected):
            self.assertEqual(found[idx]['event'], data_dict['event'])
            self.assertEqual(found[idx]['fn'], data_dict['fn'])

    @unittest.skip("TODO:")
    def test_fns_with_same_name_in_different_module_are_distinct(self):
        pass


class ClassAndObjectCallsTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.collector = Collector()

    def test_data_is_collected_when_fn_creates_obj_of_class_with_magic_init(self):
        with callspectpy.trace(self.collector):
            fn_creates_obj_of_class_A()

        found = self.collector.collected
        expected = (
            {'event': 'call', 'fn': 'fn_creates_obj_of_class_A',},
            {'event': 'call', 'fn': 'A',},
            {'event': 'return', 'fn': 'A',},
            {'event': 'call', 'fn': '__init__',},
            {'event': 'return', 'fn': '__init__',},
            {'event': 'return', 'fn': 'fn_creates_obj_of_class_A',},
        )
        for idx, data_dict in enumerate(expected):
            self.assertEqual(found[idx]['event'], data_dict['event'])
            self.assertEqual(found[idx]['fn'], data_dict['fn'])

    def test_data_is_collected_when_fn_calls_method_of_obj(self):
        with callspectpy.trace(self.collector):
            fn_calls_method_of_obj_of_class_A()

        found = self.collector.collected
        expected = (
            {'event': 'call', 'fn': 'fn_calls_method_of_obj_of_class_A',},
            {'event': 'call', 'fn': 'A',},
            {'event': 'return', 'fn': 'A',},
            {'event': 'call', 'fn': 'print',},
            {'event': 'return', 'fn': 'print',},
            {'event': 'return', 'fn': 'fn_calls_method_of_obj_of_class_A',},
        )
        for idx, data_dict in enumerate(expected):
            self.assertEqual(found[idx]['event'], data_dict['event'])
            self.assertEqual(found[idx]['fn'], data_dict['fn'])

    def test_data_is_collected_when_obj_method_calss_module_fn(self):
        with callspectpy.trace(self.collector):
            fn_calls_method_which_calls_module_fn()

        found = self.collector.collected
        expected = (
            {'event': 'call', 'fn': 'fn_calls_method_which_calls_module_fn',},
            {'event': 'call', 'fn': 'A',},
            {'event': 'return', 'fn': 'A',},
            {'event': 'call', 'fn': 'call_module_fn',},
            {'event': 'call', 'fn': 'single_call',},
            {'event': 'return', 'fn': 'single_call',},
            {'event': 'return', 'fn': 'call_module_fn',},
            {'event': 'return', 'fn': 'fn_calls_method_which_calls_module_fn',},
        )
        for idx, data_dict in enumerate(expected):
            self.assertEqual(found[idx]['event'], data_dict['event'])
            self.assertEqual(found[idx]['fn'], data_dict['fn'])

    @unittest.skip("TODO: fix it, this calls only A once, why?")
    def test_data_is_collected_when_fn_creates_two_obj_of_same_class(self):
        with callspectpy.trace(self.collector):
            fn_creates_two_objs_of_same_class()

        found = self.collector.collected
        expected = (
            {'event': 'call', 'fn': 'fn_creates_two_objs_of_same_class',},
            {'event': 'call', 'fn': 'A',},
            {'event': 'return', 'fn': 'A',},
            {'event': 'call', 'fn': 'A',},
            {'event': 'return', 'fn': 'A',},
            {'event': 'return', 'fn': 'fn_creates_two_objs_of_same_class',},
        )
        for idx, data_dict in enumerate(expected):
            self.assertEqual(found[idx]['event'], data_dict['event'])
            self.assertEqual(found[idx]['fn'], data_dict['fn'])


class Trace2FileTest(unittest.TestCase):
    def test_data_is_stored_at_passed_path(self):
        dst = tempfile.mkstemp()[1]
        with callspectpy.trace2file(dst):
            single_call()

        with open(dst) as fptr:
            lines = fptr.readlines()

        self.assertEqual(len(lines), 2)
        self.assertIn('"event": "call"', lines[0])
        self.assertIn('"event": "return"', lines[1])


if __name__ == "__main__":
    unittest.main()
