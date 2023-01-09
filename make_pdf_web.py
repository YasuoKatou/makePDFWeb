import re
from flask import Flask, request, render_template, make_response
from pathlib import Path
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/b001')
def b001():
    return app.send_static_file('bill_sample001.html')

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
@app.route('/b001/preview', methods=['POST'])
def b001_preview():
    dm = {}
    dm['details']= [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}]
    for key, val in request.form.items():
        m = _RE_DIM_CHECK_01.match(key)
        if m:
            dm['details'][int(m.group('index'))][m.group('key')] = val
            #print('index: {}, key : {}'.format(m.group('index'), m.group('key')))
        else:
            dm[key] = val
            #print('{}: {}'.format(key, val))

    r = render_template('bill_sample001.html', data=dm)
    #print(str(r))
    if 'preview' in dm:
        print('PDF : {}'.format(dm['preview']))
        return r
    return _makePDF(r)

@app.context_processor
def utility_processor():
    def format_currency(amount):
        return '{:,}'.format(int(amount)) if amount else ''
    return dict(format_currency=format_currency)

if __name__ == '__main__':
    app.run(port=8891, debug=True)

#[EOF]