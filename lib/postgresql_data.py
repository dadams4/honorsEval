import psycopg2
import psycopg2.extras
from lib.config import *

#Connecting to the database
def connectToPSQLDB():
	
	connectionString = 'dbname=%s user=%s password=%s host=%s' % (POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST)
	#print connectionString
	try:
		return psycopg2.connect(connectionString)
	except Exception as e:
	    print(type(e))
	    print(e)
	    print("Can't connect to database")
	    print("Try running 'sudo service postgresql start' in a terminal")
	    return None
		
#Code that performs the actual query
def queryDB(query, conn, select=True, args=None):
	#print("Executing a query")
	
	cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
	results = None
	
	try:
	    quer = cur.mogrify(query, args)
	    cur.execute(quer)
	    if select:
	        results = cur.fetchall()
	        
	    conn.commit()
	    
	except Exception as e:
	    conn.rollback()
	    print(type(e))
	    print(e)
	    conn.rollback()
		
	cur.close()
	return results
	
#Log in a user	
def get_login(username, password):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "select username from users where username = %s and password = crypt(%s, password)"
	#print(query_string)
	
	results = queryDB(query_string, conn, args = (username, password))
	#print(results)
	conn.close()
	return results
	
def get_name(username, password):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "select firstname from users where username = %s and password = crypt(%s, password)"
	#print(query_string)
	
	results = queryDB(query_string, conn, args = (username, password))
	#print(results)
	results = results[0]
	
	#print(results)
	conn.close()
	return results
	
def get_last_name(username, password):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "select lastname from users where username = %s and password = crypt(%s, password)"
	#print(query_string)
	
	results = queryDB(query_string, conn, args = (username, password))
	#print(results)
	results = results[0]
	
	#print(results)
	conn.close()
	return results

def change_password(newpassword, username):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
	query_string = "update users set password = crypt(%s, gen_salt('bf')) where username = %s"
	queryDB(query_string, conn, select = False, args = (newpassword, username))
	#print(query_string)
	conn.close()
	return 0

def upload_csv(filename):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "\copy checklist(firstname, lastname, email, dob, gpa, age) from %s delimiter ',' CSV HEADER"
	
	queryDB(query_string, conn, select = False, args = (filename))
	#print(query_String)
	conn.close()
	return 0
	
def get_five_announcements():
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "select to_char(date, 'Mon DD, YYYY') as date, to_char(time - interval '5 hours', 'HH12:MI') as time, title, message from announcements order by date desc limit 5"
	
	results = queryDB(query_string, conn, select = True, args =())
	#print(query_string)
	conn.close()
	#print(results)
	return results
	
def get_announcements():
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "select to_char(date, 'Mon DD, YYYY') as date, to_char(time - interval '5 hours', 'HH12:MI') as time, title, message, id from announcements order by date desc"
	
	results = queryDB(query_string, conn, select = True, args =())
	#print(query_string)
	conn.close()
	#print(results)
	return results

def get_announcement_title(ID):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "select title from announcements where id = %s"
	
	results = queryDB(query_string, conn, select = True, args = (ID))
	#print(results)
	conn.close()
	return results

def get_announcement_message(ID):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "select message from announcements where id = %s"
	print(query_string)
	#print(ID)
	results = queryDB(query_string, conn, select = True, args = (ID))
	print(results)
	conn.close()
	return results
	
def post_announcement(now, title, announcement):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
	
	query_string= "insert into announcements (date, time, title, message) values (%s, current_time, %s, %s)"
	
	queryDB(query_string, conn, select = False, args=(now, title, announcement))
	#print(query_string)
	conn.close()
	return 0

def edit_announcement(title, message, date, ID):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "update announcements set title = %s, message = %s, date = %s, time = current_time where id = %s"
	
	queryDB(query_string, conn, select = False, args = (title, message, date, ID))
	conn.close()
	return 0

def delete_announcement(ID):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "delete from announcements where id = %s"
	queryDB(query_string, conn, select = False, args=(ID))
	conn.close()
	return 0
	
	
def edit_FAQ(question, answer, ID):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "update faq set question = %s, answer = %s, id = %s"
	
	queryDB(query_string, conn, select = False, args = (question, answer, ID))
	conn.close()
	return 0

def delete_FAQ(ID):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "delete from faq where id = %s"
	queryDB(query_string, conn, select = False, args=(ID))
	conn.close()
	return 0
	
def get_FAQ():
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "select * from FAQ"
	
	results = queryDB(query_string, conn, select = True, args =())
	#print(query_string)
	conn.close()
	#print(results)
	return results
	
def get_faq_question(ID):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "select question from faq where id = %s"
	
	results = queryDB(query_string, conn, select = True, args = (ID))
	#print(results)
	conn.close()
	return results	

def get_faq_answer(ID):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "select answer from faq where id = %s"
	print(query_string)
	#print(ID)
	results = queryDB(query_string, conn, select = True, args = (ID))
	print(results)
	conn.close()
	return results
	
def post_FAQ(question, answer):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
	
	query_string= "insert into FAQ (question, answer) values (%s, %s)"
	
	queryDB(query_string, conn, select = False, args=(question, answer))
	#print(query_string)
	conn.close()
	return 0
	
def import_csv():

	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	#clear database before adding new stuff in	
	query_string2 = "delete from checklist"	
	queryDB(query_string2, conn, select = False, args=())
	
	
	query_string = "copy checklist from '/home/ubuntu/workspace/CSVFiles/cleanedCSV.csv' (FORMAT CSV, DELIMITER ',', HEADER)"
	queryDB(query_string, conn, select = False, args =())
	
	conn.close()
	return 0
	
def search_checklist(fname, lname):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "select * from checklist where FirstName = %s and LastName = %s"
	results = queryDB(query_string, conn, select = True, args=(fname, lname))
	#print(results)
	conn.close()
	return results
	
def add_user(email, password, fname, lname):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "insert into users values (%s, crypt(%s, gen_salt('bf')), %s, %s)"
	
	queryDB(query_string, conn, select = False, args = (email, password, fname, lname))
	
	conn.close()
	return 0
	
def find_new_users():
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "select email from checklist except all select username from users"
	
	results = queryDB(query_string, conn, select = True, args = ())
	conn.close()
	return results
	
def get_all_new_firstnames(email):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "select FirstName from checklist where email = %s"
	
	results = queryDB(query_string, conn, select = True, args = (email))
	results = str(results)
	conn.close()
	return results

def get_all_new_lastnames(email):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "select LastName from checklist where email = %s"
	
	results = queryDB(query_string, conn, select = True, args = (email))
	results = str(results)
	conn.close()
	return results