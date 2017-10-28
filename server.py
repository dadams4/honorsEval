import os
import subprocess
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, session, request, redirect, url_for
from flask_uploads import UploadSet, configure_uploads
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "/home/ubuntu/workspace/CSVFiles"
ALLOWED_EXTENSIONS = set(['csv'])

UPLOADS_DEFAULT_DEST = "/home/ubuntu/workspace/CSVFiles"
files = UploadSet('files', ("csv"))

app = Flask(__name__)
app.secret_key = os.urandom(24).encode('hex')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOADS_DEFAULT_DEST'] = UPLOADS_DEFAULT_DEST

configure_uploads(app, files)

from lib.config import *
from lib import postgresql_data as pg

#Currently logged in user (one per session)
logged = ''
announcements = ''

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def fix_endline(src_filename, target_filename):
    
    #s = '"\\n\"'
    s = '\\'
    print(s)
    with open(src_filename, 'r') as f:
    
        with open(target_filename, 'w') as t:
            
            for line in f:
                
                t.write(line.strip() + s + '\n')

    f.close()
    
def replace_first_line(src_filename, target_filename, replacement_line):
    f = open(src_filename)
    
        
    first_line, remainder = f.readline(), f.read()
    t = open(target_filename,"w")
    
    t.write(replacement_line + '\n')
    t.write(remainder)
            
    t.close()

@app.route('/', methods = ['GET', 'POST'])
def mainIndex():
    
    return render_template('login.html')

#This page is for posting announcements
@app.route('/announcements', methods = ['GET'])
def annoucementsPage():
    
    #Prevents page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
    
    announcement_result = pg.get_five_announcements()
    
    return render_template('announcements.html', announcements = announcement_result)

#This handles the posting of announcements
@app.route('/announcement_posted', methods = ['POST'])
def announcementsPosted():
    
    now = "now()"
    
    if request.method == 'GET':
        
        return render_template("error.html")
        
    announcement_result = pg.get_five_announcements()
    
    pg.post_announcement(now, request.form['title'], request.form['announcement'])
    
    return render_template('announcementposted.html', announcements = announcement_result)

@app.route('/announcements_full', methods = ['GET'])
def announcementsfullPage():
    
    if request.method == 'GET':
        try:
            if not session['userName']:
                
                return render_template("error.html")
                
        except KeyError:
            
            return render_template("error.html")
            
    announcement_result = pg.get_announcements()
    
    return render_template('announcements_full.html', announcements = announcement_result)

@app.route('/about', methods = ['GET'])
def aboutPage():
    
    #Prevents page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
            
    announcement_result = pg.get_five_announcements()
    
    return render_template('contact_us.html', announcements = announcement_result)

@app.route('/help', methods = ['GET'])
def helpPage():
    
    #Prevents page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
    
    announcement_result = pg.get_five_announcements()
    
    return render_template('help_screen.html', announcements = announcement_result)
    
@app.route('/upload', methods = ['GET', 'POST'])
def uploadPage():
    
    #TODO: Convert CSV file to SQL and update the database - some of this will need to be done in postgresql_data.py
    
    #TODO: Add error handling for when a user uploads a file that is not .CSV (reload page with an error alert)
    
    #Prevents page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
    
        #Prevents non-admins from reaching upload screen.  Will update with Jeanne's credentials when they are created.
        if session['userName'] != "dadams@umw.edu" and session['userName'] != "awoodruf@umw.edu" and session['userName'] != "jhurnyak@umw.edu" and session['userName'] != "adyke@mail.umw.edu":
            
            return render_template("autherror.html")
        
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            
            flash('No selected file')
            
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            
            filename = secure_filename(file.filename)
            
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            replace_first_line("/home/ubuntu/workspace/CSVFiles/" + filename, "/home/ubuntu/workspace/CSVFiles/cleanedCSV.csv", "LastName,FirstName,ID,email,Admitted,duPontCode,Status,Term,CoCur1,Date1,FSEMHN,FSEMDate,HNcourse1,HN1Date,HNcourse2,HN2Date,HNcourse3,HN3Date,HNcourse4,HN4Date,HNcourse5,HN5Date,ResearchCourse,ResearchDate,CapstoneCourse,CapstoneDate,HONR201,HONR201Date,Leadership,mentoring,HONRPortfolio4,HONRPortfolio1,HONRPortfolio2,HONRPortfolio3,ExitInterview")
            
            #fix_endline("/home/ubuntu/workspace/CSVFiles/cleanedCSV.csv", "/home/ubuntu/workspace/CSVFiles/actuallycleanedCSV.csv")
            
            subprocess.call(["sed", "-i", 's/\r//', '/home/ubuntu/workspace/CSVFiles/cleanedCSV.csv'])
            #subprocess.call(["sed 's/\r//' /home/ubuntu/workspace/CSVFiles/cleanedCSV.csv /home/ubuntu/workspace/CSVFiles/actuallycleanedCSV.csv "], shell = True)
            
            pg.import_csv()

    announcement_result = pg.get_five_announcements()
            
    return render_template('upload.html', announcements = announcement_result)

@app.route('/uploadconfirm', methods = ['POST'])
def confirmUploadPage():
    
    #Bad practice should validate input to ensure non-malicious files    
    
    print(request.form['file'])
    
    file = open(request.form['file'], r)
    
    pg.upload_csv(file)
    
    return render_template('upload.html')

#Handles administrator searching of a student's records
@app.route('/search', methods = ['POST'])
def searchChecklist():
    
    #Prevents page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
            
    student_to_search = request.form['name']
    email_to_search = request.form['email']
            

@app.route('/changepasswordform', methods = ['GET'])
def updatePasswordFormPage():
    
    #Prevents page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
    
    announcement_result = pg.get_five_announcements()
    
    return render_template('passwordchange.html', announcements = announcement_result)
    
#Ready for test
@app.route('/changepassword', methods = ['POST', 'GET'])
def updatePasswordPage():

    if request.method == 'POST':
    
        announcement_result = pg.get_five_announcements()
        
        if request.form['password1'] != request.form['password2']:
        
            return render_template('passwordchange.html', announcements = announcement_result)
    
        else:
            
            
            pg.change_password(request.form['password2'], session['userName'])
            
            name = pg.get_name(session['userName'], request.form['password2'])
            
            return render_template("index.html", logged = name, announcements = announcement_result)
            
    else:
        
        return render_template("error.html")

#Ready for test
@app.route('/logout', methods = ['POST', 'GET'])
def logOut():
    
    if request.method == 'GET':
        
        return render_template("error.html")
    
    session.clear()
    
    return render_template("login.html")
    
@app.route('/home', methods = ['GET','POST'])
def landingPage():

    #Prevents page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
    
    #Creating the current session    
    if request.method == 'POST':
        
        session['userName'] = request.form['username']
        session['passWord'] = request.form['password']
    
    if 'userName' in session:
        user = [session['userName'], session['passWord']]
        
    else:
        user = ['','']
    
    #for debugging purposes    
    print(session['userName'] + " Has logged in")
    
    result = pg.get_login(session['userName'], session['passWord'])
    
    announcement_result = pg.get_five_announcements()
    
    if not result:
        
        session['userName'] = ''
        session['passWord'] = ''
        return render_template('login.html')
    
    name = pg.get_name(session['userName'], session['passWord'])
    
    return render_template('index.html', logged=name, announcements = announcement_result)

if __name__ == '__main__':
    
    app.run(host=os.getenv('IP', '0.0.0.0'), port = int(os.getenv('PORT', 8080)), debug = True)