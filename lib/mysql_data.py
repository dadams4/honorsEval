import psycopg2
import psycopg2.extras
from lib.config import *

#Need to make this file compatible with MySQL -- Currently is only functional with PostgreSQL


#Connecting to the database
def connectToPSQLDB():
	
	connectionString = 'dbname=%s user=%s password=%s host=%s' % (POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST)
	print connectionString
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
	print("Executing a query")
	
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
		
	query_string = "select username from users where username = %s and password = SHA1(%s)"
	print(query_string)
	
	results = queryDB(query_string, conn, args = (username, password))
	print(results)
	conn.close()
	return results
	
def get_name(username, password):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "select firstname from users where username = %s and password = SHA1(%s)"
	print(query_string)
	
	results = queryDB(query_string, conn, args = (username, password))
	print(results)
	results = results[0]
	
	print(results)
	conn.close()
	return results
	
def get_last_name(username, password):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "select lastname from users where username = %s and password = SHA1(%s"
	print(query_string)
	
	results = queryDB(query_string, conn, args = (username, password))
	print(results)
	results = results[0]
	
	print(results)
	conn.close()
	return results
	
def change_password(newpassword, username):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
	query_string = "update users set password = SHA1(%s) where username = %s"
	queryDB(query_string, conn, select = False, args = (newpassword, username))
	print(query_string)
	conn.close()
	return 0
#Incomplete	
def upload_csv(filename):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "\copy checklist(firstname, lastname, email, dob, gpa, age) from %s delimiter ',' CSV HEADER"
	
	queryDB(query_string, conn, select = False, args = (filename))
	print(query_String)
	conn.close()
	return 0
	
def get_five_announcements():
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "select to_char(date, 'Mon DD, YYYY') as date, to_char(time, 'HH12:MI') as time, title, message from announcements order by date desc limit 5"
	
	results = queryDB(query_string, conn, select = True, args =())
	#print(query_string)
	conn.close()
	#print(results)
	return results
	
def get_announcements():
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "select to_char(date, 'Mon DD, YYYY') as date, to_char(time, 'HH12:MI') as time, title, message from announcements order by date desc"
	
	results = queryDB(query_string, conn, select = True, args =())
	#print(query_string)
	conn.close()
	print(results)
	return results
	
def post_announcement(now, title, announcement):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
	
	query_string= "insert into announcements (date, time, title, message) values (%s, current_time, %s, %s)"
	
	results = queryDB(query_string, conn, select = False, args=(now, title, announcement))
	print(query_string)
	conn.close()
	return results
	
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
	print(results)
	conn.close()
	return results
	
def add_user(email, password, fname, lname):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "insert into users values (%s, SHA1(%s)), %s, %s)"
	
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