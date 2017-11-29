# honorsEval
<h1>Honors Program Degree Evaluation for CPSC 430 at University of Mary Washington</h1>

<h2>Project Background:</h2>
<h3>Honors Program Degree Evaluation Client: Ms. Jeanne Campbell Email: jcampbe2@umw.edu</h3>
<li>Students in the honors program need to complete certain requirements to remain in the program and ultimately earn their Honors Diploma.</li> 
<li>Details of the program requirements can be found here: http://academics.umw.edu/honorsprogram/honors-program-requirements/</li> 
<li>This project involves creating a web accessible version of the Honor’s Program Checksheet.</li>  
<li>Ideally this program will allow administrators to update the requirements met for all students (by uploading Excel data) and allow students to login and check on their own progress in the program.</li> 
<li>A template of the currently used checksheet is available here: http://academics.umw.edu/honorsprogram/files/2012/03/Honor-Program-Requirements-Checksheet_14_15.pdf</li>
<br>
<p><b>Created by Daniel Adams, Aaron Dyke, Adam Hurnyak, and Andrew Woodruff</b></p>


<h2>Installation Instructions:</h2>

<h3>Always run first:</h3>
<p>sudo apt-get update</p>
<p>sudo apt-get upgrade</p>

<h3>Packages:</h3>

<p>sudo easy_install flask markdown</p>
<p>sudo apt-get install python-setuptools</p>
<p>sudo apt-get install postgresql</p>
<p>sudo apt-get install python-psycopg2</p>


<h3>Google Cloud Only:</h3>

<p>sudo apt-get install gunicorn</p>
<p>sudo apt-get install supervisor</p>


<h3>To enter Postgres:</h3>

<h4>First time:</h4> 

<p>sudo sudo -u postgres psql</p>
<p>\password <your password here></p>

<h3>All other times:</h3>

<p>psql -U postgres -h localhost</p>

<br>

<p><a href="35.199.60.177">Example of this app running online</a></p>
