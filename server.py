import os
import re
import datetime
import subprocess
import uuid
import smtplib
import psycopg2
import psycopg2.extras
from lib.config import *
from flask import Flask, render_template, session, request, redirect, url_for, current_app
from flask_uploads import UploadSet, configure_uploads
from werkzeug.utils import secure_filename
import flask_login
#from pdfjinja import PdfJinja

UPLOAD_FOLDER = "/home/ubuntu/workspace/CSVFiles"
ALLOWED_EXTENSIONS = set(['csv'])

UPLOADS_DEFAULT_DEST = "/home/ubuntu/workspace/CSVFiles"
files = UploadSet('files', ("csv"))

#pdfjinja = PdfJinja('form.pdf', current_app.jinja_env)

app = Flask(__name__)
app.secret_key = os.urandom(24).encode('hex')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOADS_DEFAULT_DEST'] = UPLOADS_DEFAULT_DEST

configure_uploads(app, files)

from lib.config import *
from lib import postgresql_data as pg

#Global variables passed by the server to html pages
logged = ''
announcements = ''
searchedResults = ''
password_success = False
isAdmin = True

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=20)
    session.modified = True
    user = flask_login.current_user
    
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

def send_email(recip, message):
    
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.ehlo()
    smtp_server.starttls()
    smtp_server.login('danieladamsumw@gmail.com', APP_PASSWORD)
    
    smtp_server.sendmail('danieladamsumw@gmail.com', recip, message)
    smtp_server.quit()
    
    print("Email sent to " + str(recip))
    
def new_user_email():
    
    #This block creates new users and then emails them their login credentials
            new_users = pg.find_new_users()
            
            for email in new_users:
                
                #Get the user info and add it to the database
                fname = pg.get_all_new_firstnames(email)
                lname = pg.get_all_new_lastnames(email)
                rand_pass = str(uuid.uuid4())[0:8]
                
                fname = fname[3:-3]
                lname = lname[3:-3]
                               
                pg.add_user(str(email)[2:-2], rand_pass, fname, lname)
                        
                #WARNING.  IF THE LINES BELOW THIS ARE UNCOMMENTED THEY WILL SEND EMAILS TO ALL STUDENTS IN THE CSV FILE UPON SUCCESSFUL UPLOAD.  MAKE SURE IT IS COMMENTED OUT WHEN TESTING CSV UPLOADING, OR USE A SEPARATE CSV FILE.
                
                message_body = """Subject: Welcome to UMW Honors Degree Evaluation\nHello, and welcome to UMW Honors Program Degree evaluation.\nPlease navigate to https://honorseval1-aarondyke.c9users.io to log in. Your username is your full UMW email and your temporary password is """ +  rand_pass +  """. Please change your password once you log in for the first time.\n\nThank you,\n\nUMW Honors Degree Evaluation Team"""
                send_email(email, message_body)

def password_reset_email(email):
    
    rand_pass = str(uuid.uuid4())[0:8]
    
    message_body = """Subject: Password reset request for UMW Honors Degree Evaluationn\nHello, you are receiving this email because you requested a password change for your account.\nYour new password is: """ +  rand_pass +  """. Please navigate to https://honorseval1-aarondyke.c9users.io to log in. Please change your password once you log in.\n\nThank you,\n\nUMW Honors Degree Evaluation Team"""
    
    send_email(email, message_body)
    pg.change_password(rand_pass, email)


def validate_password(password):

    if re.search(r"[a-z]", password) is None or re.search(r"[A-Z]", password) is None or re.search(r"\d", password) is None or len(password) < 8 or len(password) > 30:
        return False
    else:
        return True

#Keeps administrator resources from being rendered for non-admin users
def check_admin():
    
    if session['userName'] != "dadams@umw.edu" and session['userName'] != "awoodruf@umw.edu" and session['userName'] != "jhurnyak@umw.edu" and session['userName'] != "adyke@mail.umw.edu" and session['userName'] != "test_user":
        
        isAdmin = False
    else:
        isAdmin = True
        
    return isAdmin
    
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
    
    #Prevents non-admins from reaching upload screen.  Will update with Jeanne's credentials when they are created.
    if check_admin() == False:
            
        return render_template("autherror.html")
    
    announcement_result = pg.get_five_announcements()
    isAdmin = check_admin()
    
    return render_template('announcements.html', announcements = announcement_result, admin = isAdmin)

#This handles the posting of announcements
@app.route('/announcement_posted', methods = ['POST' , 'GET'])
def announcementsPosted():
    
    now = "now()"
    
    if request.method == 'GET':
        
        return render_template("error.html")
        
    announcement_result = pg.get_five_announcements()
    
    pg.post_announcement(now, request.form['title'], request.form['announcement'])
    isAdmin = check_admin()
    
    return render_template('announcementposted.html', announcements = announcement_result, admin = isAdmin)

@app.route('/announcements_full', methods = ['GET'])
def announcementsfullPage():
    
    if request.method == 'GET':
        try:
            if not session['userName']:
                
                return render_template("error.html")
                
        except KeyError:
            
            return render_template("error.html")
            
    announcement_result = pg.get_announcements()
    isAdmin = check_admin()
    
    return render_template('announcements_full.html', announcements = announcement_result, admin = isAdmin)

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
    isAdmin = check_admin()
    
    return render_template('contact_us.html', announcements = announcement_result, admin = isAdmin)

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
    FAQ_result = pg.get_FAQ()
    isAdmin = check_admin()
    
    return render_template('help_screen.html', announcements = announcement_result, FAQ = FAQ_result, admin = isAdmin)

#This handles the posting of announcements
@app.route('/FAQ_posted', methods = ['GET', 'POST'])
def FAQPosted():
    
    #Prevents page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
       
        return render_template("error.html")
        
    announcement_result = pg.get_five_announcements()
    
    pg.post_FAQ(request.form['question'], request.form['answer'])
    isAdmin = check_admin()
    
    return render_template('FAQposted.html', announcements = announcement_result, admin = isAdmin)
    
@app.route('/upload', methods = ['GET', 'POST'])
def uploadPage():
    
    #Prevents page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
    
    #Prevents non-admins from reaching upload screen.  Will update with Jeanne's credentials when they are created.
    if check_admin() == False:
            
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
            
            subprocess.call(["sed", "-i", 's/\r//', '/home/ubuntu/workspace/CSVFiles/cleanedCSV.csv'])

            pg.import_csv()
            
            #WARNING.  IF THE LINE BELOW THIS is UNCOMMENTED it WILL SEND EMAILS TO ALL STUDENTS IN THE CSV FILE UPON SUCCESSFUL UPLOAD.  MAKE SURE IT IS COMMENTED OUT WHEN TESTING CSV UPLOADING, OR USE A SEPARATE CSV FILE.
            new_user_email()
    
    announcement_result = pg.get_five_announcements()
    isAdmin = check_admin()
    
    return render_template('upload.html', announcements = announcement_result, admin = isAdmin)

#This just uploads the file I think unless the above function actually does that
@app.route('/uploadconfirm', methods = ['POST', 'GET'])
def confirmUploadPage():
    
    if request.method == 'GET':
        
        return render_template("error.html")
    
    print(request.form['file'])
    
    file = open(request.form['file'], r)
    
    pg.upload_csv(file)
    
    return render_template('upload.html')

#Handles administrator searching of a student's records
@app.route('/search', methods = ['GET'])
def searchChecklist():
    
    #Prevents page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
    
    #Prevents non-admins from reaching upload screen.  Will update with Jeanne's credentials when they are created.
        if check_admin() == False:
            
            return render_template("autherror.html")
    
    #TODO: Populate the html with this data 
    announcement_result = pg.get_five_announcements()
    isAdmin = check_admin()
    
    return render_template('search.html', announcements = announcement_result, admin = isAdmin)        
    
@app.route('/searchresults', methods = ['POST', 'GET'])
def searchResultsPage():
    
    #Prevents page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
       
       return render_template('error.html')  
    
    if request.method == 'POST':
        
        announcement_result = pg.get_five_announcements()
        isAdmin = check_admin()
        
        name_to_search = request.form['fname']
        
        lname_to_search = request.form['lname']
        
        name_to_search = name_to_search.title()
        lname_to_search = lname_to_search.title()
        
        #email_to_search = request.form['email']
        searchedResults = pg.search_checklist(name_to_search, lname_to_search)
        
        if not searchedResults:

            return render_template('search.html', announcements = announcement_result, admin = isAdmin, searched = searchedResults)
    
        else:    
        
            return render_template('adminchecklistview.html', announcements = announcement_result, admin = isAdmin, searched = searchedResults)

@app.route('/view', methods = ['GET'])
def viewChecklist():
    
    #Prevents page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
            
    announcement_result = pg.get_five_announcements()
    isAdmin = check_admin()
    
    fname = pg.get_name(session['userName'], session['passWord'])
    lname = pg.get_last_name(session['userName'], session['passWord'])
    
    fname = unicode(fname)[2:-2]
    lname = unicode(lname)[2:-2]
    
    print(fname + " " + fname)
    
    searchedResults = pg.search_checklist(fname, lname)
    
    return render_template("studentchecklistview.html", announcements = announcement_result, admin = isAdmin, searched = searchedResults)

@app.route('/passwordresetform', methods = ['GET', 'POST'])
def resetPasswordForm():
    
    return render_template('resetpassword.html')

@app.route('/passwordreset', methods = ['POST', 'GET'])
def resetPassword(user_email):
    
    password_reset_email(request.form['email'])
    
    return render_template('resetpassword.html', youremail = request.form['email'])
        
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
    isAdmin = check_admin()
    
    return render_template('passwordchange.html', announcements = announcement_result, admin = isAdmin)
    
#Ready for test
@app.route('/changepassword', methods = ['POST', 'GET'])
def updatePasswordPage():

    isAdmin = check_admin()

    if request.method == 'POST':
    
        announcement_result = pg.get_five_announcements()
        
        if request.form['password1'] != request.form['password2']:
        
            return render_template('passwordchange.html', announcements = announcement_result, admin = isAdmin)
            
        elif not validate_password(request.form['password1']):
        
            return render_template('passwordchange.html', announcements = announcement_result, admin = isAdmin)
    
        else:
            
            pg.change_password(request.form['password2'], session['userName'])
            
            name = pg.get_name(session['userName'], request.form['password2'])
            
            password_success = True
            
            session['passWord'] = request.form['password2']
            
            return render_template("passwordchange.html", logged = name, announcements = announcement_result, admin = isAdmin, pass_ = password_success)
            
    else:
        
        return render_template("error.html")

#Ready for test
@app.route('/logout', methods = ['POST', 'GET'])
def logOut():
    
    #Prevents page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
            
    session.clear()
    
    return render_template("login.html")

@app.route('/removeannouncement', methods = ['POST', 'GET'])
def removeAnnouncement():
    
    #Prevents page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        
        return render_template("error.html")
    
    #Prevents non-admins from reaching upload screen.  Will update with Jeanne's credentials when they are created.
    if check_admin() == False:
            
        return render_template("autherror.html")
    
    announcement_result = pg.get_five_announcements()
    isAdmin = check_admin()
    
    print(request.form['remove'])
    name = pg.get_name(session['userName'], session['passWord'])
    
    ID = request.form['remove']
    ID = (ID, )
    
    pg.delete_announcement(ID)
    
    return render_template('index.html', logged = name, announcements = announcement_result, admin = isAdmin)

@app.route('/removeFAQ', methods = ['POST', 'GET'])
def removeFAQ():
    
    #Prevents page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        
        return render_template("error.html")
    
    #Prevents non-admins from reaching upload screen.  Will update with Jeanne's credentials when they are created.
    if check_admin() == False:
            
        return render_template("autherror.html")
        
    announcement_result = pg.get_five_announcements()
    isAdmin = check_admin()
    
    print(request.form['remove'])
    name = pg.get_name(session['userName'], session['passWord'])
    
    ID = request.form['remove']
    ID = (ID, )
    
    pg.delete_FAQ(ID)
    
    return render_template('help_screen.html', logged = name, announcements = announcement_result, admin = isAdmin)
    
@app.route('/editannouncement', methods = ['POST', 'GET'])
def editAnnouncement():
    
    #Prevents page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
    
    #Prevents non-admins from reaching upload screen.  Will update with Jeanne's credentials when they are created.
    if check_admin() == False:
            
        return render_template("autherror.html")
    
    announcement_result = pg.get_five_announcements()
    isAdmin = check_admin()
    
    ID = request.form['edit']
    ID = (ID, )
    
    title = pg.get_announcement_title(ID)
    message = pg.get_announcement_message(ID)
    
    title = unicode(title)[3:-3]
    message = unicode(message)[3:-3]
    
    return render_template('editannouncement.html', announcements = announcement_result, admin = isAdmin, t = title, m = message, edit = ID )

@app.route('/editannouncementconfirm', methods = ['POST', 'GET'])
def editAnnouncementConfirm():
    
    if request.method == 'GET':
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
    
    #Prevents non-admins from reaching upload screen.  Will update with Jeanne's credentials when they are created.
    if check_admin() == False:
            
        return render_template("autherror.html")
            
    announcement_result = pg.get_five_announcements()
    isAdmin = check_admin()
    
    ID = request.form['id'][3:-3]
    now = 'now()'
    
    pg.edit_announcement(request.form['title'], request.form['announcement'], now, ID)
    
    return render_template("announcements_full.html", announcements = announcement_result, admin = isAdmin)

@app.route('/editFAQ', methods = ['POST', 'GET'])
def editFAQ():
    
    #Prevents page from being rendered unless it is being accessed through a valid session
    if request.method == 'GET':
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
    
    #Prevents non-admins from reaching upload screen.  Will update with Jeanne's credentials when they are created.
    if check_admin() == False:
            
        return render_template("autherror.html")
    
    announcement_result = pg.get_five_announcements()
    isAdmin = check_admin()
    
    ID = request.form['edit']
    ID = (ID, )
    
    title = pg.get_faq_question(ID)
    message = pg.get_faq_answer(ID)
    
    title = unicode(title)[3:-3]
    message = unicode(message)[3:-3]
    
    return render_template('editFAQ.html', announcements = announcement_result, admin = isAdmin, t = title, m = message, edit = ID )

@app.route('/editFAQconfirm', methods = ['GET', 'POST'])
def editFAQConfirm():
    
    if request.method == 'GET':
        try: 
            if not session['userName']:
        
                return render_template("error.html")
        
        except KeyError:
        
            return render_template("error.html")
    
    #Prevents non-admins from reaching upload screen.  Will update with Jeanne's credentials when they are created.
    if check_admin() == False:
            
        return render_template("autherror.html")
            
    announcement_result = pg.get_five_announcements()
    isAdmin = check_admin()
    
    ID = request.form['id'][3:-3]
    now = 'now()'
    
    pg.edit_FAQ(request.form['title'], request.form['announcement'], ID)
    
    return render_template("help_screen.html", announcements = announcement_result, admin = isAdmin)

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
    
    print(session['userName'] + " Has logged in")
    
    result = pg.get_login(session['userName'], session['passWord'])
    
    isAdmin = check_admin()
    
    announcement_result = pg.get_five_announcements()
    
    if not result:
        
        session['userName'] = ''
        session['passWord'] = ''
        return render_template('login.html')
    
    name = pg.get_name(session['userName'], session['passWord'])
    
    return render_template('index.html', logged=name, announcements = announcement_result, admin = isAdmin)

if __name__ == '__main__':
    
    app.run(host=os.getenv('IP', '0.0.0.0'), port = int(os.getenv('PORT', 8080)), debug = True)