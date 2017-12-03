import json
import re


DATA_SET_LIMIT = 1024


class Merger:
    def __init__(self, show_modules=None, data_set_limit=None):
        self.show_modules = show_modules or []
        self.data_set_limit = data_set_limit or DATA_SET_LIMIT

    def parse_from_path(self, path):
        with open(path) as fptr:
            self.parse(fptr)

    def parse(self, filelike):
        idx = 0
        for json_dict in filelike.readlines():
            data_dict = json.loads(json_dict)
            event = data_dict['event']
            #TODO: inform & allow user to opt-in long running rendering of seq-diag
            if self.show_modules and data_dict['module'] not in self.show_modules:
                continue

            #TODO: data_dict which events=return and theirs counterpart with
            # event=call are on stack should be processed anyway
            in_storage = True
            if idx >= self.data_set_limit and not in_storage:
                continue

            if event == 'call':
                self.handle_call(data_dict)
            elif event == 'return':
                self.handle_return(data_dict)
            else:
                raise ValueError("Expected events: 'call', 'return', got: {!r}".format(event))
            idx += 1

    def handle_call(self, data_dict):
        pass

    def handle_return(self, data_dict):
        pass

    def merged(self):
        pass


class MergerToSeqDiag(Merger):
    def __init__(self, show_modules=None, data_set_limit=DATA_SET_LIMIT):
        super().__init__(show_modules, data_set_limit)
        self.storage = [{'entity_path': 'MainThread'}]
        self.result_data = []

    def call_args_as_lines(self, args):
        if isinstance(args, dict):
            result = '\\n'.join(
                ("{!r}: {!r}".format(n, v) for n, v in args.items())
            ) or '{}'
        else:
            result = repr(args)
        return result

    def handle_call(self, data_dict):
        call_args = data_dict.get('call_args', '<C2S_MISSING>')

        self.result_data.append({
            'event': data_dict['event'],
            'left': self.escape(self.storage[-1]['entity_path']),
            'right': self.escape(data_dict['entity_path']),
            #TODO: new lines renders bad sometimes
            #'help': self.escape(self.call_args_as_lines(call_args)),
            'help': self.escape(str(call_args)),
        })
        self.storage.append(data_dict)

    def handle_return(self, data_dict):
        current = self.storage.pop()
        self.result_data.append({
            'event': data_dict['event'],
            'left': self.escape(current['entity_path']),
            'right': self.escape(self.storage[-1]['entity_path']),
            'help': self.escape(str(data_dict.get('return_value', ''))),
        })

    def merged(self):
        if not self.result_data:
            #TODO: this starts to be buggy when using with self.single_actor
            result = 'participant MainThread'
        else:
            result = []
            for idx, pair in enumerate(self.result_data):
                arrow = "->" if pair['event'] == 'call' else '-->'
                result.append(
                    "{}{}{}: {}".format(
                        pair['left'], arrow, pair['right'], pair['help'],
                    )
                )
            result = '\n'.join(result)
        return result

    def single_actor(self, actor):
        result = []
        for data in self.result_data:
            found = data['left'] == actor or data['right'] == actor
            if found:
                result.append(data)
        self.result_data = result

    def escape(self, text):
        #TODO: make js-sequece-diagram escaping chars and use it here, instead
        # of erasing

        # comma removes dot, wtf Oo
        return re.sub(r'[:-><]', '', text) or ''


class MergerToCallTree(Merger):
    def __init__(self, show_modules=None, data_set_limit=DATA_SET_LIMIT):
        super().__init__(show_modules, data_set_limit)
        self.result_dict = [{'label': 'MainThread', 'children': []}]

    def handle_call(self, data_dict):
        self.result_dict.append(
            {'label': data_dict['entity_path'], 'children': []}
        )

    def handle_return(self, data_dict):
        last = self.result_dict.pop()
        self.result_dict[-1]['children'].append(last)

    def merged(self):
        return self.result_dict


class MergerToFlatDict(Merger):
    def __init__(self, show_modules=None, data_set_limit=DATA_SET_LIMIT):
        super().__init__(show_modules, data_set_limit)
        self.result_dict = {}  # actor: data

    def handle_call(self, data_dict):
        #TODO: what about mainthread?
        self.result_dict[data_dict['entity_path']] = data_dict

    def merged(self):
        return self.result_dict
