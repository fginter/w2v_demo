# Rahti deployment cheat sheet (w2v_demo)

App runs on CSC Rahti (OpenShift/OKD). Word-vector models live on a persistent
volume mounted at `/data` (env `W2V_DATA_DIR=/data`). Models are listed in
`/data/models.yaml`. NOTE: mount must be read-write — lwvlib opens model files
with `r+b`.

## Login

1. https://rahti.csc.fi → web console → username (top right) → **Copy login command** → Display Token

## Routine redeploy (code changed)

```
git push                       # push to the fork Rahti builds from (branch: master)
oc start-build w2v-demo       # or set up a GitHub webhook to trigger automatically
oc logs -f bc/w2v-demo        # watch build
oc get pods                   # new pod rolls out on image change
```

Plain restart without rebuild: `oc rollout restart deploy/w2v-demo`

## Full redeploy from scratch

1. Create PVC:
   ```
   oc apply -f pvc.yaml        # PVC name: flask-data, RWO, size >= models + headroom
   ```
2. Upload data via throwaway pod (PVC is RWO — app must not be running):
   ```
   oc apply -f uploader.yaml   # pod with image docker.io/instrumentisto/rsync-ssh,
                               # command "sleep infinity", PVC mounted at /data
   oc rsync ./my-data/ uploader:/data/ --no-perms     # models.yaml + .bin files
   oc delete pod uploader
   ```
3. Web console → **+** → Import from Git → fork URL, Python builder, branch `master`.
   Repo must contain `requirements.txt` and `app.sh` (gunicorn, port 8080).
4. Attach volume + env (first rollout crash-loops until this is done — expected):
   ```
   oc set volume deploy/w2v-demo --add --overwrite --name=data \
     --type=persistentVolumeClaim --claim-name=flask-data --mount-path=/data
   oc set env deploy/w2v-demo W2V_DATA_DIR=/data
   oc set resources deploy/w2v-demo --limits=memory=4Gi --requests=memory=2Gi
   ```
5. Route (if not created by the import):
   ```
   oc create route edge w2v-demo --service=w2v-demo --insecure-policy='Redirect'
   oc get route
   ```

## Adding / updating models

PVC is RWO, so stop the app first:

```
oc scale deploy/w2v-demo --replicas=0
oc apply -f uploader.yaml
oc rsync ./new-models/ uploader:/data/ --no-perms   # new .bin files + updated models.yaml
oc exec uploader -- cat /data/models.yaml           # sanity check
oc delete pod uploader
oc scale deploy/w2v-demo --replicas=1
```

Bigger models ⇒ check memory limit (`oc set resources`, watch for OOMKilled).
models.yaml entry format:

```yaml
- name: "Display name"
  location: file.bin          # relative to /data
  enable: true
```

## Debugging order

```
oc logs -f bc/w2v-demo        # build problems (deps, submodule)
oc logs deploy/w2v-demo -f    # app problems (models.yaml, paths, OOM)
oc describe pod <pod>         # mount/scheduling/OOMKilled
oc rsh <pod>                  # shell inside the pod
```
