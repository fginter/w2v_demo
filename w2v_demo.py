from wvlib_light import wvlib
from flask import Flask
import flask
import json

app = Flask("wv_demo")

@app.route("/")
def index():
    return flask.render_template("index_template.html")

@app.route('/nearest',methods=["POST"])
def nearest():
    word=flask.request.form['word'].strip()
    N=int(flask.request.form['topn'])
    top_n=wv.nearest(word,N)
    if top_n is None:
        tbl=flask.render_template("empty_result_tbl.html",word=word)
    else:
        top_n_words=[w for s,w in top_n]
        tbl=flask.render_template("result_tbl.html",words=top_n_words)
    return json.dumps({'tbl':tbl});

@app.route('/analogy',methods=["POST"])
def analogy():
    src1=flask.request.form['analogy_src1'].strip()
    target1=flask.request.form['analogy_target1'].strip()
    src2=flask.request.form['analogy_src2'].strip()
    N=int(flask.request.form['analogy_topn'])
    top_n=wv.analogy(src1,target1,src2,N)
    if top_n is None:
        tbl=flask.render_template("empty_result_tbl.html",word=u" and ".join(w for w in (src1,target1,src2) if w not in wv.w_to_dim))
    else:
        top_n_words=[w for s,w in top_n]
        tbl=flask.render_template("result_tbl.html",words=top_n_words)
    return json.dumps({'tbl':tbl});


#Init stuff (I'm sure there's a better way)
wv=wvlib.WV.load("pb34_wf_200_v2.bin",400000,3000000)

if __name__ == '__main__':
    app.run(debug=True)
