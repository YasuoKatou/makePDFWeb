import re
from flask import Flask, request, render_template, make_response
from pathlib import Path
import subprocess

app = Flask(__name__)

def getClientUri():
    p = request.headers.getlist("Request-Path")
    return '/' if len(p) == 0 else p[0]

@app.route('/')
def index():
    data = {'request_uri': getClientUri()}
    return render_template('index.html', data=data)

@app.route('/b<string:pid>')
def b_pid(pid):
    u = getClientUri()
    if u == '/':
        u = '/b{}'.format(pid)
    data = {'request_uri': u}
    return render_template('bill_sample' + pid + '_inp.html', data=data)

def _makePDF(html):
    hp = Path('./tmp/test.html')
    hp.parent.mkdir(parents=True, exist_ok=True)
    with hp.open(mode='w', encoding='utf-8') as f:
        f.write(html)

    cmd = [
        'wkhtmltopdf',
        './tmp/test.html',
        './tmp/test.pdf',
    ]
    subprocess.run(cmd, capture_output=True, text=True)

    r = make_response()
    r.data = open('./tmp/test.pdf', 'rb').read()
    r.mimetype = 'application/pdf'
    return r

_RE_DIM_CHECK_01 = re.compile(r'details\[(?P<index>\d+)\]\[(?P<key>\w+)+\]$')
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

    r = render_template('bill_sample' + pid + '.html', data=dm)
    #print(str(r))
    if 'preview' in dm:
        print('PDF : {}'.format(dm['preview']))
        return r
    return _makePDF(r)

@app.context_processor
def utility_processor():
    def format_currency(amount):
        return '{:,}'.format(int(amount)) if amount else ''
    def format_date(dt):
        return dt.replace('-', '/')
    return dict(format_currency=format_currency, format_date=format_date)

if __name__ == '__main__':
    app.run(port=8891, debug=True)

#[EOF]