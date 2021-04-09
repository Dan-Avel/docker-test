from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.route('/')
@app.route('/<name>')
def helloWorld(name=None):
	return render_template('hello.html', name=name)
