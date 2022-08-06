# Import dependencies
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# -------------------------------------------------------------------------
# Sources for this file:
# o Module 9 online material: Throughout (except as otherwise noted);
# o Bootcamp class Zoom instruction(# also see note immediately following):
#   - Coding method to put `session = Session(engine)` and `session.close`
#     pair within each route function
#   - <br/> to separate text into lines
# o TA office hours: determining where in statistics route to put
#   `session = Session(engine)` and `session.close` pair so that results
#   returned appropriately 
# -------------------------------------------------------------------------

# --Set Up the Database
# . Access the SQLite database
engine = create_engine("sqlite:///hawaii.sqlite")

# . Reflect the database into our classes
Base = automap_base()
# _ Python Flask function to reflect the tables into SQLAlchemy
Base.prepare(engine, reflect=True)

# print(Base.classes.keys()) #--xxx: was for testing

# . With the database reflected, save references to each table;
# use variables to be referenced later
Measurement = Base.classes.measurement
Station = Base.classes.station

# -- Move commented-out code below to within the specific route code
#    --> moves from browser to standard output terminal window the
#        ProgrammingError message (both SQLAlchemy and SQLite) where
#        the thread changes from where the SQLite object is created
#        (can only use a SQLite object in same thread where created)
# # . Create a session link from Python to database
# session = Session(engine)

# --Set Up Flask
# Create a new Flask instance called `app`,
# being sure to pass Python **magic method** `__name__`
# . All routes go after next line, or code may not run properly
app = Flask(__name__)

# = Routes defined below =
# Define the **root** (highest level of hierarchy) starting point
# . Next line is the "welcome" route, essentially the homepage
# NOTE as each route is created, align code to left to avoid errors
@app.route("/")
def welcome():
    msg = '''
        !! Welcome to the Climate Analysis API !!<br/>\
        Available Routes:<br/>\
        /api/v1.0/precipitation<br/>\
        /api/v1.0/stations<br/>\
        /api/v1.0/tobs<br/>\
        /api/v1.0/temp/start/end\
        '''    
    return ( msg
        # f"Welcome to the Climate Analysis API!<br/>"
        # f"Available Routes:<br/>"
        # f"/api/v1.0/precipitation<br/>"
        # f"/api/v1.0/stations<br/>"
        # f"/api/v1.0/tobs<br/>"
        # f"/api/v1.0/temp/start/end"
    )

# . Create precipitation route
# _ (a) set variable to year ago from most recent date in database
# _ (b) write query to get date and precipitation for that prior year
# _ (c) create dictionary with date as the key, precipitation as the value
# Note `Jsonify()` is a function that converts the dictionary to a JSON file
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    print("Server received request for 'precipitation' page...")

    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365) #_(a)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all() #_(b)
    precip = {date: prcp for date, prcp in precipitation} #_(c)
    
    session.close
    return jsonify(precip)

# . Create Stations Route
# _ [a] query to get all of the stations in database
# _ [b1] "unravel" results into a one-dimensional array;
# _ [b2] converting that array into a list
# _ [c] jsonify the [b] list to return it as JSON
# Note `Jsonify()` function here converts the list to a JSON file
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    print("Server received request for 'stations' page...")

    results = session.query(Station.station).all() #_[a]
    stations = list(np.ravel(results)) #_[b]

    session.close
    return jsonify(stations=stations)

# . Create monthly temperature observations ('tobs') route
# _ {a} create function called `temp_monthly()`;
# _ {b1} calculate date one year ago from last date in the database,
#        note this is same one calculated previously--in precipitation route;
# _ {b2} query primary station for all tobs from previous year;
# _ {c} as before (stations route), unravel results to 1D array, converting to list
# Note that `jsonify()` here is to convert {c} list to JSON format
@app.route("/api/v1.0/tobs")
def temp_monthly():
    session = Session(engine)
    print("Server received request for 'tobs' page...")

    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365) #_{b1}
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all() #_{b2}
    temps = list(np.ravel(results)) #_{c}
    
    session.close
    return jsonify(temps=temps)

# . Create Statistics Route
# _ <a> create the route;
# _ <b> provide both a starting and ending date;
# _ <c> create a function `stats()` to put our code in;
# _ <d1> create list `sel`, for results of data points to collect;
# _ <d2> create the query to get the statistics data
# Note (*) next to `sel` list to indicate multiple results for query:
# : minimum, average, and maximum temperatures
@app.route("/api/v1.0/temp/<start>") #_<a>
@app.route("/api/v1.0/temp/<start>/<end>") #_<b>
def stats(start=None, end=None):
    session = Session(engine)
    print("Server received request for 'statistics' page...")

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs),\
           func.max(Measurement.tobs)] #_<d1>

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all() #_<d2>
        temps = list(np.ravel(results))

        session.close
        return jsonify(temp_stats=temps)
        
    results = session.query(*sel).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all() #_<d2>
    temps = list(np.ravel(results))

    session.close
    return jsonify(temp_stats=temps)

# ------------------------
# Define main behavior
if __name__ == "__main__":
    app.run(debug=True)