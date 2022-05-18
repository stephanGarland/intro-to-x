#!/usr/bin/env python

from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def form():
    return render_template("index.html")

@app.route("/", methods=["POST"])
def form_post():
    return request.form["echo_input"]

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
