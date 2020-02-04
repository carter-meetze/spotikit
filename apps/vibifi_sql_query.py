import mysql.connector
from pprint import pprint as pprint


mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    passwd="btbam1207",
    database="sys",
    auth_plugin="mysql_native_password"
)

mycursor = mydb.cursor()

query = "SELECT AVG(valence) FROM sys.astrolifi WHERE user_name = '1243461497'"

mycursor.execute(query)

myresult = mycursor.fetchall()

pprint(myresult)

