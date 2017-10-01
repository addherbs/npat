from flask import Flask, render_template, request, redirect, make_response
app = Flask(__name__)



# this route is defined as the route for the main/index page
@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('server.html')


#Causes the app to start
if __name__ == '__main__':
    app.run()
