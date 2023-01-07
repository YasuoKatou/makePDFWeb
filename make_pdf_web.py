import re
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/b001')
def b001():
    return app.send_static_file('bill_sample001.html')

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
    return r

if __name__ == '__main__':
    app.run(port=8891, debug=True)

#[EOF]