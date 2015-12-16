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
    top_n=wv.nearest(word,10)
    if top_n is None:
        tbl=u"This word is not in the vocabulary, sorry..."
    else:
        top_n_words=[w for s,w in top_n]
        tbl=flask.render_template("result_tbl.html",words=top_n_words)
    return json.dumps({'tbl':tbl});


#Init stuff (I'm sure there's a better way)
wv=wvlib.WV.load("pb34_wf_200_v2.bin",10000,100000)

if __name__ == '__main__':
    app.run(debug=True)
