#!/usr/bin/env python
# coding: utf-8

# In[6]:


import pyrebase
import pymysql
from pymysql.cursors import DictCursor        
        


# In[2]:


get_ipython().system('pip install --upgrade cryptography pyOpenSSL')


# In[ ]:





# In[10]:


# Firebase configuration
firebase_config = {
  "apiKey": "AIzaSyAJ5aZBMHsf6qLr1YFlsWYHePmkdcsyEys",
  "authDomain": "doyenifypanelapi.firebaseapp.com",
  "databaseURL": "https://console.firebase.google.com/u/0/project/doyenifypanelapi/firestore/databases/-default-/data/~2FRegistration~2F00jWDpnVsiNUK2NKjMFw",
  "projectId": "doyenifypanelapi",
  "storageBucket": "doyenifypanelapi.appspot.com",
  "messagingSenderId": "446515177325",
  "appId": "1:446515177325:web:52dd67b9715e2f55ffdc64",
  "measurementId": "G-4HJEC3D27H"
}




        


# In[21]:


# Initialize Firebase
firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

# MySQL connection
mysql_connection = pymysql.connect(
    host='locahost',
    user='doyenify001',
    password='facebook',
    db='DoyenifyProject1',
    port=3306
    
)
cursor = mysql_connection.cursor()


# In[ ]:


# Function to insert data into MySQL
def insert_data_to_mysql(data):
    with mysql_connection.cursor() as cursor:
        sql = "INSERT INTO Registrationportal (Date, Full Name, Email, Phone, Course, Currency, Course Price, Paid (%), User Country, Status, Cohort) VALUES (%s, %s)"
        cursor.execute(sql, (data['field1'], data['field2'],data['field3'],
                             data['field4'],data['field5'],data['field6'],
                             data['field7'], data['field8'],data['field9'], data['field10'],data['field11'], data['field12']))
        mysql_connection.commit()

# Firebase listener for data changes
def stream_handler(message):
    print("Received message:", message["event"])  # can be 'put', 'patch', etc.
    print("Path:", message["path"])  # relative to the database root
    print("Data:", message["data"])  # new data at the location
    if message["data"]:
        insert_data_to_mysql(message["data"])

# Start streaming data from Firebase
my_stream = db.child("your_firebase_child_path").stream(stream_handler)

try:
    while True:
        pass  # Keep the script running to listen for updates
except KeyboardInterrupt:
    print("Stopping stream...")
    my_stream.close()
    mysql_connection.close()


# In[ ]:




