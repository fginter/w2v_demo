from wvlib_light import lwvlib
from flask import Flask
import flask
import json
import yaml

MAX_RANK_MEM=5000
MAX_RANK=10000
# DEBUGMODE=False  #set in config_local
AUTOCOMPLETE_PREF=2
AUTOCOMPLETE_MAX_SUGGESTIONS=5

try:
    from config_local import * #use to override the constants above if you like
except ImportError:
    pass #no config_local

app = Flask(__name__)

@app.route("/")
def index():
    global model_names
    return flask.render_template("index_template.html",model_names=model_names)

def build_autocomplete_index(wv):
    """builds a simple autocomplete dictionary"""
    wv.autocomplete_index={} #key: prefix of length pref, value: all words that start with the prefix in order of frequency
    for w in wv.words:
        if len(w)<AUTOCOMPLETE_PREF:
            continue
        wv.autocomplete_index.setdefault(w[:AUTOCOMPLETE_PREF],[]).append(w)
    

@app.route('/autocomplete',methods=['GET'])
def autocomplete():
    global loaded_models
    search = flask.request.args.get('term')
    model_name = flask.request.args.get('model_name')
    wv=loaded_models[model_name]
    result=[]
    if search in wv.w_to_dim: #always make sure the search is there if it's a word
        result.append(search)
    for s in wv.autocomplete_index.get(search[:AUTOCOMPLETE_PREF],[]):
        if s!=search and s.startswith(search):
            result.append(s)
            if len(result)>AUTOCOMPLETE_MAX_SUGGESTIONS:
                break
    return json.dumps(result)


def val2dict(val):
    # This is what the request values look like
    # {'form[1][name]': 'topn', 'form[1][value]': '10', 'model_name': 'Finnish 4B lemmas skipgram', 'form[0][name]': 'word', 'form[0][value]': 'a'}
    #
    # And we want this:
    # {'topn':'10','word':'a','model_name':'...'}
    res={}
    for k,v in val.items():
        if k.endswith("[value]"):
            name=val[k.replace("[value]","[name]")]
            res[name]=v
        elif k.endswith("[name]"):
            pass
        else:
            res[k]=v
    return res
            
            

@app.route('/nearest',methods=["POST"])
def nearest():
    global loaded_models
    values=val2dict(flask.request.values)
    word=values['word'].strip()
    model_name=values['model_name']
    N=int(values['topn'])
    wv=loaded_models[model_name]
    top_n=wv.nearest(word,N)
    if top_n is None:
        tbl=flask.render_template("empty_result_tbl.html",word=word)
    else:
        top_n_words=[w for s,w in top_n]
        tbl=flask.render_template("result_tbl.html",words=top_n_words)
    return json.dumps({'tbl':tbl});

@app.route('/analogy',methods=["POST"])
def analogy():
    global loaded_models
    values=val2dict(flask.request.values)
    src1=values['analogy_src1'].strip()
    target1=values['analogy_target1'].strip()
    src2=values['analogy_src2'].strip()
    N=int(values['analogy_topn'])
    wv=loaded_models[values['model_name']]
    top_n=wv.analogy(src1,target1,src2,N)
    if top_n is None:
        tbl=flask.render_template("empty_result_tbl.html",word=" and ".join(w for w in (src1,target1,src2) if w not in wv.w_to_dim))
    else:
        top_n_words=[w for s,w in top_n]
        tbl=flask.render_template("result_tbl.html",words=top_n_words)
    return json.dumps({'tbl':tbl});

@app.route('/similarity',methods=["POST"])
def similarity():
    global loaded_models
    values=val2dict(flask.request.values)
    w1=values['similarity_w1'].strip()
    w2=values['similarity_w2'].strip()
    wv=loaded_models[values['model_name']]
    sim=wv.similarity(w1,w2)
    if sim is None:
        tbl=flask.render_template("empty_result_tbl.html",word=" and ".join(w for w in (w1,w2) if w not in wv.w_to_dim))
    else:
    	tbl=flask.render_template("result_tbl.html",words=[str(sim)])
    return json.dumps({'tbl':tbl});


#Init stuff (I'm sure there's a better way)
loaded_models={} #name -> wv
model_names=[]   #list of names in order of appearance
with open("models.yaml") as f:
    models=yaml.load(f)
    for m in models:
        if not m.get("enable",True):
            continue
        loaded_models[m["name"]]=lwvlib.WV.load(m["location"],m.get("MAX_RANK_MEM",MAX_RANK_MEM),m.get("MAX_RANK",MAX_RANK))
        model_names.append(m["name"])
        build_autocomplete_index(loaded_models[m["name"]])

if __name__ == '__main__':
    app.run(debug=DEBUGMODE)
