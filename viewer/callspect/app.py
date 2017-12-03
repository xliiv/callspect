import os

import flask

from callspect import config, utils


app = flask.Flask(__name__)
app.config.from_mapping(config.config_dict, verbose=1)
if not app.config['TESTING']:
    flat_dict = utils.MergerToFlatDict()
    flat_dict.parse_from_path(app.config['CALLSPECT_DATA_PATH'])
    actor2data = flat_dict.merged()


# TODO: mv views to views.py
@app.route("/")
def index():
    #TODO: data validation with wtfforms?
    #TODO: too much copy-and-paste with within API views
    data = dict(
        sequence_url=flask.url_for(
            'call_tree',
            show_modules=flask.request.args.getlist('show_modules', None),
            data_set_limit=int(flask.request.args.get('data_set_limit', 1024)),
        ),
        seq_diag_url=flask.url_for('seq_diag'),
        src_code_url=flask.url_for('src_code'),
    )
    return flask.render_template('index.html', **data)


@app.route('/api/call-tree')
def call_tree():
    #TODO: data validation with wtfforms
    data = dict(
        show_modules=flask.request.args.getlist('show_modules', None),
        data_set_limit=int(flask.request.args.get('data_set_limit', 1024)),
    )

    call_tree = utils.MergerToCallTree(**data)
    call_tree.parse_from_path(app.config['CALLSPECT_DATA_PATH'])

    data = {
        'status': 'success', # 'error'
        'data': { # dict when success or string when error
            'callTree': call_tree.merged(),
        }
    }
    return flask.jsonify(data)


@app.route('/api/seq-diag')
def seq_diag():
    actor = flask.request.values.get('actor', None)
    if not actor:
        return {'status': 'error', 'data': 'Param "actor" missing'}
    data = dict(
        #TODO: data validation with wtfforms
        show_modules=flask.request.args.getlist('show_modules', None),
        data_set_limit=int(flask.request.args.get('data_set_limit', 1024)),
    )
    seq_diag = utils.MergerToSeqDiag(**data)
    seq_diag.parse_from_path(app.config['CALLSPECT_DATA_PATH'])
    seq_diag.single_actor(actor)
    data = {
        'status': 'success',
        'data': seq_diag.merged(),
    }
    return flask.jsonify(data)


@app.route('/api/src-code')
def src_code():
    actor = flask.request.values.get('actor', None)
    if not actor:
        return {'status': 'error', 'data': 'Param "actor" missing'}
    data = dict(
        #TODO: data validation with wtfforms
        show_modules=flask.request.args.getlist('show_modules', None),
        data_set_limit=int(flask.request.args.get('data_set_limit', 1024)),
    )
    file_content = ""
    actor_data = actor2data.get(actor, {})
    file_path = actor_data.get('abs_filepath', None)
    try:
        with open(file_path) as fptr:
            file_content = fptr.read()
    except FileNotFoundError:
        file_content = ""
    data = {
        'status': 'success',
        'data': {
            'filePath': file_path,
            'fileContent': file_content,
            'lineNumber': actor_data.get('line_number', None),
            'fileType': "python",
        },
    }
    return flask.jsonify(data)
