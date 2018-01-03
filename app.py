#app.py

# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session, flash, json
from functools import wraps
import sqlite3
from forms import SignupForm
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import math
from random import *
import random
import scipy.spatial as spatial
import matplotlib.patches as patches
import pylab
import StringIO
import base64
from io import BytesIO

# create the application object
app = Flask(__name__)

# config
app.secret_key = 'my precious'


# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


# use decorators to link the function to a url
@app.route('/')
@login_required
def home():
    return render_template('index.html')
    
@app.route('/results',methods = ['POST', 'GET'])
@login_required
def results():
    if request.method == 'POST':
        result = request.form

        ##actual percolation code that i put here even though i probs wasn't meant to but it works so hey ho
    gridSize = 100   #set grid size
    p=float(result['P'])
    r=float(result['R'])
    t=float(result['T'])
    if 0<p<=1 and 1<=r<=10 and 1<=t:
        def getNeighbours(point_tree, points):
            global neighbours
            neighbours=[]
            for i in range(0,len(settings)-1):
                neighbours.append(point_tree.query_ball_point(points[i], r))
        ##grid initiation
        def gridSetup():
            coords=[]   #coords is list of all grid square co-ordinates
            for i in range(1,gridSize+1):
                for j in range(1,gridSize+1):
                    coords.append((i,j))    #loops through every cell and adds to coords
            global points
            points=np.array(coords)
            global settings
            settings=[0]*len(coords) #settings is activation of each cell relevant to coords
            if p!=1:
                randomIndexes=random.sample(range(1, len(coords)), int(round((gridSize**2)*p)))
            else:
                randomIndexes=points
            for i in range(0,len(randomIndexes)-1):     #set random cells as potential (1) according to p value
                element=randomIndexes[i]-1
                settings[element]=1
            randomPoint=[0,0]
            while randomPoint[0]<r or randomPoint[0]>gridSize-r or randomPoint[1]<r or randomPoint[1]>gridSize-r:
                randomStart=randint(1, len(settings))-1 #find random initialise cell to activate
                randomPoint=coords[randomStart]
            global point_tree 
            point_tree = spatial.cKDTree(points)    #create array of coords for radius finding
            getNeighbours(point_tree, points)
            firstNeighbours = neighbours[randomStart]
            for i in range(0,len(firstNeighbours)):
                settings[firstNeighbours[i]]=2  #set start point and neighbours as active (3)
        def percolate():
            origSettings=0
            x=np.array(settings)
            x==1
            global offs
            offs=np.nonzero(x==1)[0]
            while origSettings!=settings:
                origSettings=list(settings)
                for i in offs:
                    nearestNeighbours = neighbours[i]
                    neighbourSettings=[]
                    for j in range(0,len(nearestNeighbours)):
                        neighbourSettings.append(settings[nearestNeighbours[j]])
                    count = neighbourSettings.count(2)
                    if count >= t:
                        settings[i]=2
        def smoothing():
            origSettings=0
            x=np.array(settings)
            x==1
            greys=np.nonzero(x==0)[0]
            for i in greys:
                nearestNeighbours = neighbours[i-1]
                neighbourSettings=[]
                for j in range(0,len(nearestNeighbours)):
                    neighbourSettings.append(settings[nearestNeighbours[j]])
                countOn = neighbourSettings.count(2)
                countOff = neighbourSettings.count(1)
                if countOn>countOff:
                    settings[i]=2
                else:
                    settings[i]=1
        #run code
        gridSetup()
        percolate()
        smoothing()
        #get base64
        fig = plt.figure()       
        ax1 = fig.add_subplot(111, aspect='equal')
        for i in range(0,len(settings)):
            if settings[i]==1:
                ax1.add_patch(
                patches.Rectangle(
                    (points[i,0]-1, points[i,1]-1), 1, 1, facecolor = "black", edgecolor="none") ) 
        pylab.ylim([0,gridSize])
        pylab.xlim([0,gridSize])
    #        plt.savefig('/figure.png')
        figfile = BytesIO()
        plt.savefig(figfile, format='png')
        figfile.seek(0)
        figdata_png = base64.b64encode(figfile.getvalue())
        resultsBase = figdata_png
        return render_template("results.html",result=result, resultsBase=resultsBase)

    else:
        flash('Please input valid parameter values')
        return redirect(url_for('home'))

@app.route('/viewImages')
@login_required
def viewImages():
    return render_template('viewImages.html')  # render a template

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template

# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
			session['logged_in'] = True
			flash('You were logged in.')
			return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'GET':
        return render_template('signup.html', form = form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            if 'user already exist in database':
                return "Email address already exists"
            else:
                return "will create user here"
        else:
            return "Form didn't validate"

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('welcome'))


# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)