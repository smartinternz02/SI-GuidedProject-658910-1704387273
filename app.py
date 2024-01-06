import numpy as np
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.application.inception_v3 import preprocess_input import requests
from flask import Flask, request, render_template,redirect, url_for
from cloudant.client import cloudant

model=load_model(r"ibm xception model.h5")
app = Flask(__name__)

from cloudant.client import cloudant
client=cloudant.iam('USERNAME','APIKEY',connect=True)

my_database=client.create_database('my_database')

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def regsiter():
    if request.method == "POST":
        uname = request.form['sname']
        email = request.form['semail']
        pword = request.form['spassword']
        role = request.form['role']
        print(uname,email,pword,role)
        sql = "SELECT * FROM NEC REGISTER WHERE USERNAME=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt, 1, uname)
        ibm_db.execute(stmt)
        out = ibm_db.fetch_assoc(stmt)
        print(out)
        if out != False:
            msg = "Already Registered"
            return render_template("register.html",msg = msg)
        else:
            sql = "INSERT INTO REGISTER VALUES(?,?,?,?)"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, uname)
            ibm_db.bind_param(stmt, 2,email)
            ibm_db.bind_param(stmt, 3, pword)
            ibm_db.bind_param(stmt, 4, role)
            ibm_db.execute(stmt)
            msg = "Registered"
            return render_template("register.html", msg =msg)

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        global uname
        uname = request.form['USERNAME']
        pword = request.form['PWD']
        print(uname, pword)
        sql = "SELECT * FROM NEC WHERE USERNAME = ? AND PASSWORD = ?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt, 1, uname)
        ibm_db.bind_param(stmt,2,pword)
        ibm_db.execute(stmt)
        out = ibm_db.fetch_assoc(stmt)
        print(out)
        if out != False:
            session['username'] = uname
            session['emailid'] = out['EMAILID']
            
            if out['ROLE'] == 0:
                return render_template("prediction.html",username = uname, emailid = out['EMAILID'] )
            else: 
                return render_template("logout.html",username = uname, emailid = out['EMAILID'])
        else: 
            msg = "Invalid Credentials"
            return render_template("login.html",message1= msg)
    return render_template("login.html")

@app.route('/logout')
def logout():
    return render_template("logout.html")

@app.route('/predict',methods=['GET','POST'])
def upload():
    if request.method=='POST':
        f=request.files['image']
        basepath=os.path.dirname(__file__)
        filepath=os.path.join(basepath,'uploads',f.filename)
        f.save(filepath)
        img=image.load_img(filepath,target_size=(64,64))
        x=image.img_to_array(img)
        x=np.expand_dims(x,axis=0)
        pred=np.argmax(model.predict(x),axis=1)
        index=['No disease visible','NPDR','Moderate NPDR','Severe NPDR','PDR']
        text="The Classified Disease is : " +str(index[pred[0]])
    return text

if __name__ == "__main__":
    app.run(debug=True)