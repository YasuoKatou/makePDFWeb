from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/b001')
def b001():
    return app.send_static_file('bill_sample001.html')

@app.route('/b001/preview', methods=['POST'])
def b001_preview():
    #for key, val in request.form.items():
    #    print('{}: {}'.format(key, val))
    r = render_template('bill_sample001.html', data=request.form)
    #print(str(r))
    return r

if __name__ == '__main__':
    app.run(port=8891, debug=True)

#[EOF]