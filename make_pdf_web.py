import re
from flask import Flask, request, render_template, make_response
from pathlib import Path
import subprocess
from datetime import datetime
import uuid
import json

_PROJECT_ROOT = Path(__file__).parent
_TMP_PATH = Path(_PROJECT_ROOT / 'tmp')
_TMP_PATH.mkdir(mode=0o777, parents=True, exist_ok=True)
_COOKIES_PATH = Path(_PROJECT_ROOT / 'cookies')
_COOKIES_PATH.mkdir(mode=0o777, parents=True, exist_ok=True)

app = Flask(__name__)

def getClientUri():
    p = request.headers.getlist("Request-Path")
    return '/' if len(p) == 0 else p[0]

@app.route('/')
def index():
    data = {'request_uri': getClientUri()}
    rt = render_template('index.html', data=data)
    uid = request.cookies.get('uid', None)
    if uid:
        #print('uid : {}'.format(uid))
        return rt
    uid = str(uuid.uuid4())
    resp = make_response(rt)
    max_age = 60 * 60 * 24 * 120 # 120 days
    expires = int(datetime.now().timestamp() + max_age)
    resp.set_cookie('uid', value=uid, max_age=max_age, expires=expires)
    return resp

@app.route('/b<string:pid>')
def b_pid(pid):
    uid = request.cookies.get('uid', None)
    #print('uid : {}'.format(uid))
    u = getClientUri()
    if u == '/':
        u = '/b{}'.format(pid)
    data = loadSession('b'+pid, uid)
    data['request_uri'] = u

    return render_template('bill_sample' + pid + '_inp.html', data=data)

def _makePDF(html, uid):
    hp = Path(_TMP_PATH / (uid + '.html'))
    hp.write_text(html, encoding='utf-8')

    pp = Path(_TMP_PATH / (uid + '.pdf'))
    cmd = [
        'wkhtmltopdf',
        '--disable-smart-shrinking',
        str(hp.absolute()),
        str(pp.absolute()),
    ]
    subprocess.run(cmd, capture_output=True, text=True)

    r = make_response()
    with pp.open(mode='rb') as f:
        r.data = f.read()
    r.mimetype = 'application/pdf'
    return r

_RE_DIM_CHECK_01 = re.compile(r'details\[(?P<index>\d+)\]\[(?P<key>\S+)+\]$')
@app.route('/b<string:pid>/preview', methods=['POST'])
def b001_preview(pid):
    dm = {}
    dm['details']= []
    for key, val in request.form.items():
        m = _RE_DIM_CHECK_01.match(key)
        if m:
            idx = int(m.group('index'))
            if len(dm['details']) < (idx + 1):
                dm['details'].append({})
            dm['details'][idx][m.group('key')] = val
            #print('index: {}, key : {}'.format(m.group('index'), m.group('key')))
        else:
            dm[key] = val
            #print('{}: {}'.format(key, val))
    uid = request.cookies.get('uid', None)
    saveSession('b'+pid, uid, dm)

    r = render_template('bill_sample' + pid + '.html', data=dm)
    #print(str(r))
    if 'preview' in dm:
        print('PDF : {}'.format(dm['preview']))
        return r
    return _makePDF(r, uid)

@app.context_processor
def utility_processor():
    def format_currency(amount):
        return '{:,}'.format(int(amount)) if amount else ''
    def format_date(dt):
        return dt.replace('-', '/')
    return dict(format_currency=format_currency, format_date=format_date)

def loadSession(pid, uid):
    p = Path(_PROJECT_ROOT / 'cookies' / uid)
    if p.exists():
        s = p.read_text(encoding='utf-8')
        j = json.loads(s)
        if pid in j:
            return j[pid]
    return {}

def saveSession(pid, uid, data):
    p = Path(_COOKIES_PATH / uid)
    if p.exists():
        s = p.read_text(encoding='utf-8')
        d = json.loads(s)
    else:
        d = {}
    d[pid] = data
    p.write_text(json.dumps(d), encoding='utf-8')

if __name__ == '__main__':
    app.run(port=8891, debug=True)

#[EOF]