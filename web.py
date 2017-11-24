from flask import Flask
from flask import render_template
from flask import request
from compiler import lexer
app = Flask(__name__)


lexer_engine = lexer.LexerEngine()

@app.route("/")
def show_lexer():
    return render_template('lexer.html')


@app.route("/api/v1/lexer", methods=['POST'])
def api_lexer():
    ret, error = lexer_engine.process(request.form['code'])
    return ret + error


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)