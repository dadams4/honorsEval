import psycopg2
import psycopg2.extras
from lib.config import *

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
		
	query_string = "select username from users where username = %s and password = crypt(%s, password)"
	print(query_string)
	
	results = queryDB(query_string, conn, args = (username, password))
	print(results)
	conn.close()
	return results
	
def get_name(username, password):
	
	conn = connectToPSQLDB()
	if conn == None:
		return None
		
	query_string = "select firstname from users where username = %s and password = crypt(%s, password)"
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
		
	query_string = "update users set password = crypt(%s, gen_salt('bf')) where username = %s"
	queryDB(query_string, conn, select = False, args = (newpassword, username))
	print(query_string)
	conn.close()
	return 0