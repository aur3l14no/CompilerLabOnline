from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from toy import lexer, opg
from compiler.parser import Parser, OpCode, PCode
from compiler.interpreter import Interpreter
from compiler.exceptions import *
import sys

app = Flask(__name__)

PORT = 4000

lexer_engine = lexer.LexerEngine()


# @app.route("/")
@app.route("/lexer")
def show_lexer():
    return render_template('lexer.html')


@app.route("/opg")
def show_opg():
    return render_template('opg.html')


@app.route("/")
@app.route("/parser")
def show_parser():
    return render_template('parser.html')


@app.route("/interpreter")
def show_interpreter():
    return render_template('interpreter.html')


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
        program = request.form['code'].strip()
        opg_engine.import_rules(raw_rules)
        if opg_engine.calc_priority_tab():
            opg_engine.print_priority_tab()
            print()
            opg_engine.analyse(program)
    # print(s.getvalue())
    return s.getvalue()


@app.route("/api/v1/parser", methods=['POST'])
def api_parser():
    s = StringIO()
    t = StringIO()
    with redirect_stdout(s), redirect_stderr(t):
        parser = Parser()
        program = request.form['code'].strip()
        parser.load_program(program)
        parser.analyze()
    if t.getvalue() != '':
        return t.getvalue()
    else:
        return s.getvalue()


@app.route("/api/v1/interpreter", methods=['POST'])
def api_interpreter():
    pcodes = []
    s = StringIO()
    t = StringIO()
    interpreter = Interpreter()
    with redirect_stdout(s), redirect_stderr(t):
        ln = 0
        program = request.form['code'].strip()
        interpreter.in_ = request.form['in'].strip().split()
        try:
            for line in program.split('\n'):
                ln += 1
                line = line.strip(' \r()')
                pieces = line.split(',')
                pcodes.append(PCode(OpCode[pieces[0].strip()], int(pieces[1].strip()), int(pieces[2].strip())))
            interpreter.interpret(pcodes)
        except Exception:
            print('Unexpected p-code at %d' % ln, file=sys.stderr)
    if t.getvalue() != '':
        return t.getvalue()
    else:
        return s.getvalue()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
