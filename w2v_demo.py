from wvlib_light import lwvlib
from flask import Flask
import flask
import json

MAX_RANK_MEM=100000
MAX_RANK=300000
DEBUGMODE=False
AUTOCOMPLETE_PREF=2
AUTOCOMPLETE_MAX_SUGGESTIONS=5

try:
    from config_local import * #use to override the constants above if you like
except ImportError:
    pass #no config_local

app = Flask("wv_demo")

@app.route("/")
def index():
    return flask.render_template("index_template.html")

def build_autocomplete_index(wv):
    """builds a simple autocomplete dictionary"""
    global autocomplete_index
    autocomplete_index={} #key: prefix of length pref, value: all words that start with the prefix in order of frequency
    for w in wv.words:
        if len(w)<AUTOCOMPLETE_PREF:
            continue
        autocomplete_index.setdefault(w[:AUTOCOMPLETE_PREF],[]).append(w)

@app.route('/autocomplete',methods=['GET'])
def autocomplete():
    global autocomplete_index
    search = flask.request.args.get('term')
    result=[]
    for s in autocomplete_index.get(search[:AUTOCOMPLETE_PREF],[]):
        if s.startswith(search):
            result.append(s)
            if len(result)>AUTOCOMPLETE_MAX_SUGGESTIONS:
                break
    return json.dumps(result)

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
wv=lwvlib.WV.load("pb34_wf_200_v2.bin",MAX_RANK_MEM,MAX_RANK)
build_autocomplete_index(wv)

if __name__ == '__main__':
    app.run(debug=DEBUGMODE)
