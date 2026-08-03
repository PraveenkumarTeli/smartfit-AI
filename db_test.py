import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Pmteli@123",
    database="smartfit_db"
)

print("Connected successfully!")
cursor=conn.cursor()
cursor.execute("insert into workouts(exercise,reps,date) values(%s,%s,%s)",("bicep_curl",2,"2028-08-02"))
conn.commit()
conn.close()