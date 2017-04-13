from flask import Flask,render_template

app=Flask(__name__)

@app.route('/', methods=['GET'])
def index():
	images = "Ye image wo image"
	return render_template('index.html', images=images)

if __name__=='__main__':
    app.run(debug=True)