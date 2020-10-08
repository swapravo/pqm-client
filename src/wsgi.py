from os import urandom
from flask import Flask, request, redirect, url_for, abort, render_template, flash, session
# session USES COOKIES! THESE COOKIES USE TRADITIONAL SIGNATURE SCHEMES


app = Flask(__name__)
# print("Do I need this?")
app.secret_key = urandom(24)


@app.route('/')
def hello_world():
	return "Home Page!"


@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != "abc":
			error = 'Invalid username'
		elif request.form['password'] != "xyz":
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return "yeyeye"
	return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    #session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
	app.debug = True
	app.run()
