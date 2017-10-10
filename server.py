import os
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, session, request

app = Flask(__name__)
app.secret_key = os.urandom(24).encode('hex')

from lib.config import *
from lib import postgresql_data as pg

#Currently logged in user
logged = ''

@app.route('/', methods = ['GET', 'POST'])
def mainIndex():
    
    
    return render_template('login.html')

@app.route('/annoucements', methods = ['GET'])
def annoucementsPage():
    
    #TODO: create announcements.html
    
    #Prevent a page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
    
    
    return render_template('announcements.html')
    
@app.route('/about', methods = ['GET'])
def aboutPage():
    
    #Prevent a page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
    
    return render_template('contact_us.html')

@app.route('/help', methods = ['GET'])
def helpPage():
    
    #Prevent a page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
    
    return render_template('help_screen.html')
    
@app.route('/upload', methods = ['GET'])
def uploadPage():
    
    #TODO: Retrieve .csv file
    
    #TODO: Convert .csv file to SQL and update the database
    
    #Prevent a page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
    
    return render_template('upload.html')
    
@app.route('/changepasswordform', methods = ['GET'])
def updatePasswordFormPage():
    
    #Prevent a page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
    
    return render_template('passwordchange.html')
    
#Ready for test
@app.route('/changepassword', methods = ['POST'])
def updatePasswordPage():

    if request.method == 'POST':

        if request.form['password1'] != request.form['password2']:
        
            return render_template('passwordchange.html')
    
        else:
        
            pg.change_password(request.form['password2'], session['userName'])
            
            name = pg.get_name(session['userName'], request.form['password2'])
            
            return render_template("index.html", logged = name)

@app.route('/logout', methods = ['POSt'])
def logOut():
    
    session.clear()
    
    return render_template("login.html")
    
@app.route('/home', methods = ['GET','POST'])
def landingPage():

    #Prevent a page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
        
    if request.method == 'POST':
        session['userName'] = request.form['username']
        session['passWord'] = request.form['password']
    
    if 'userName' in session:
        user = [session['userName'], session['passWord']]
        
    else:
        user = ['','']
    
    #for debugging purposes    
    print(user)
    
    result = pg.get_login(session['userName'], session['passWord'])
    
    if not result:
        session['userName'] = ''
        session['passWord'] = ''
        return render_template('login.html')
    
    name = pg.get_name(session['userName'], session['passWord'])
    
    return render_template('index.html', logged=name)

if __name__ == '__main__':
    
    app.run(host=os.getenv('IP', '0.0.0.0'), port = int(os.getenv('PORT', 8080)), debug = True)