import inspect
import json
import os
import sys
from contextlib import ContextDecorator


default_sys_trace = sys.gettrace()


def trace2file_start(filepath):
    formatter = FormatterJson()
    collector = CollectorFile(filepath, formatter)
    trace_start(collector)


def trace2file_stop():
    trace_stop()


class trace2file(ContextDecorator):
    def __init__(self, filepath):
        # this must be contextlib.ContextDecorator
        # contextlib.contextmanager'd be collected in tracing - pointless
        self.filepath = filepath

    def __enter__(self):
        trace2file_start(self.filepath)

    def __exit__(self, exc_type, exc, exc_tb):
        trace2file_stop()


def trace_start(collector=None):
    collector = collector or CollectorPrint()
    trace_fn = trace_fn_factory(collector)
    sys.settrace(trace_fn)


def trace_stop():
    sys.settrace(default_sys_trace)


class trace(ContextDecorator):
    def __init__(self, collector):
        # this must be contextlib.ContextDecorator
        # contextlib.contextmanager'd be collected in tracing - pointless
        self.collector = collector

    def __enter__(self):
        trace_start(self.collector)

    def __exit__(self, exc_type, exc, exc_tb):
        trace_stop()


class FormatterJson:
    def __init__(self, encoding='utf8', newline='\n'):
        self.encoding = encoding
        self.newline = newline

    def make_jsonable(self, data_dict):
        jsonable = {}
        for k, v in data_dict.items():
            try:
                json.dumps(v)
                jsonable[k] = v
            except TypeError:
                try:
                    json.dumps(repr(v))
                    jsonable[k] = repr(v)
                except Exception:
                    jsonable[k] = '<not-jsonable>'
        return jsonable

    def format(self, data_dict):
        jsonable = self.make_jsonable(data_dict)
        return (json.dumps(jsonable) + self.newline).encode(self.encoding)


class CollectorFile:
    def __init__(self, filepath, formatter):
        self.filepath = filepath
        self.file = open(self.filepath, 'wb')
        self.formatter = formatter

    def append(self, data_dict):
        line = self.formatter.format(data_dict)
        self.file.write(line)
        self.file.flush()

    def __del__(self):
        self.file.close()


class CollectorPrint:
    def append(self, data_dict):
        print(data_dict)


def get_module_name(file_path):
    """Returns module name or '' for file at `file_path`"""
    return inspect.getmodulename(file_path) if file_path else ''


def get_call_args(frame):
    """Returns dict with parameters belong to `frame`'s callable"""
    call_args = {}
    for i in range(frame.f_code.co_argcount):
        name = frame.f_code.co_varnames[i]
        call_args[name] = frame.f_locals[name]
    return call_args


def get_class_name(frame):
    """Returns class name for callable from `frame` or ''"""
    try:
        #TODO: use type() when tests are written?
        class_name = frame.f_locals['self'].__class__.__name__
    except (KeyError, AttributeError):
        class_name = ''
    return class_name


def trace_fn_factory(collector):
    def trace_fn(frame, event, arg, collector=collector):
        if event in ("call", "return"):
            module = inspect.getmodule(frame.f_code)
            if (
                module and module.__package__ and module.__package__ == 'callspectpy'
            ):
                # skip tracing all items from callspectpy package
                return trace_fn

            file_path = os.path.abspath(frame.f_code.co_filename)
            module_name = get_module_name(file_path)
            call_args = get_call_args(frame)

            data = dict(
                event=event,
                abs_filepath=file_path,
                line_number=frame.f_code.co_firstlineno,
                module=module_name,
                cls=get_class_name(frame),
                #TODO: obj=obj,?
                fn=frame.f_code.co_name,
                call_args=call_args,
                #TODO: package=pkg?,
            )
            #TODO: write tests for it
            #TODO: ensure that f2 defined in f1 and other m1.f2 are different entities
            # replace with? https://docs.python.org/3/glossary.html#term-qualified-name
            data['entity_path'] = '.'.join(
                [i for i in [data['module'], data['cls'], data['fn']] if i]
            )
            if event == 'return':
                data['return_value'] = arg
            if collector:
                collector.append(data)
        return trace_fn
    return trace_fn
