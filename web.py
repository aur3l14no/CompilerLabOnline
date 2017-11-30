from flask import Flask
from flask import render_template
from flask import request
from compiler import lexer
from compiler import opg
from contextlib import redirect_stdout
from io import StringIO


app = Flask(__name__)

PORT = 4000

lexer_engine = lexer.LexerEngine()


# @app.route("/")
@app.route("/lexer")
def show_lexer():
    return render_template('lexer.html')


@app.route("/")
@app.route("/opg")
def show_opg():
    return render_template('opg.html')


@app.route("/api/v1/lexer", methods=['POST'])
def api_lexer():
    s = StringIO()
    with redirect_stdout(s):
        lexer_engine.process(request.form['code'])
    return s.getvalue()


@app.route("/api/v1/opg", methods=['POST'])
def api_opg():
    s = StringIO()
    with redirect_stdout(s):
        opg_engine = opg.OPGEngine()
        raw_rules = [*request.form['grammar'].replace('\r', '').split('\n')]
        opg_engine.import_rules(raw_rules)
        opg_engine.calc_priority_tab()
        opg_engine.print_priority_tab()
        print()
        program = request.form['code'].strip()
        opg_engine.analyse(program)
    # print(s.getvalue())
    return s.getvalue()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)