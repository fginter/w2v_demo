from wvlib_light import wvlib
from flask import Flask
import flask
import json

app = Flask(__name__)

@app.route("/")
def index():
    return flask.render_template("index_template.html")

@app.route('/nearest',methods=["POST"])
def nearest():
    word=flask.request.form['word'];
    tbl=flask.render_template("result_tbl.html",words=[word,u"this",u"is",u"a",u"test"])
    return json.dumps({'tbl':tbl});



if __name__ == '__main__':
    app.run(debug=True)
