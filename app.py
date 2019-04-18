import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_
from sqlalchemy import inspect
import numpy as np
import pandas as pd
import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite", pool_pre_ping=True)
#engine = create_engine("sqlite:///../Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

from flask import Flask, json, jsonify
app = Flask(__name__)

@app.route('/')
def home_route():
    """ Available API Route Endpoints"""
    return (f"<a href=/api/v1.0/precipitation/>precipitaion</a><br><br/>" 
        f"<a href=/api/v1.0/stations/>List of stations</a><br><br/>" 
        f"<a href=/api/v1.0/tobs/>2017 JSON list of Temp Observations:</a> <br><br/>"
        f"For the following, enter date as form 'yyyy' or 'yyyy-mm' or 'yyyy-mm-dd' for BEST RESULTS! <br><br/>"
        f"Stats Combined Stations. Enter Start date:  <br/>"
        f"<a href=/api/v1.0/2016-08-01/>Start date 2016-08-01</a> <br><br/>" 
        f"Stats Combined Stations. Enter Start & End Date:  <br/>"
        f"<a href=/api/v1.0/2016-01-01/2016-12-31/>Start date: 2016-01-01 End Date: 2016-12-31</a>")
       

@app.route('/api/v1.0/precipitation/')
def precipitation():
    lastDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    lastDate = str(lastDate).strip('(,)')
    print(lastDate)
    year_ago = pd.to_datetime(lastDate) - dt.timedelta(days=365)
    print(year_ago)
    oneYear = dt.date(year_ago.year,year_ago.month, year_ago.day)
    print(oneYear)
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > oneYear).all()
    prcp_dict = dict(results)
    session.close()
    print()
    print("Results for Precipitation")
    return jsonify(prcp_dict) 

@app.route('/api/v1.0/stations/')
def stations():
    results = session.query(Station.station,Station.name).all()
    station_dict = dict(results)
    session.close()
    print()
    print("List of stations")
    return jsonify(station_dict) 

@app.route('/api/v1.0/tobs/')
def tobs():
    lastDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    lastDate = str(lastDate).strip('(,)')
    year_ago = pd.to_datetime(lastDate) - dt.timedelta(days=365)
    oneYear = dt.date(year_ago.year,year_ago.month, year_ago.day)   
    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date > oneYear).all()
    session.close()
    tobs = dict(results)
    print()
    print("Temperature Observations")
    return jsonify(tobs) 

@app.route('/api/v1.0/<start>/')
def combinedStats(start):     
    results =  session.query(Measurement.station,Station.name,func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs))\
                .outerjoin(Station, Measurement.station == Station.station).group_by(Measurement.station)\
                .filter(Measurement.date >= start).all()
    stats = list(np.ravel(results))
    session.close()
    print()
    print("Temperature Statistics")
    return jsonify(stats) 

@app.route('/api/v1.0/<start>/<end>/')
def combined_stats(start,end):
    results =  session.query(Measurement.station,Station.name,func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs))\
                .outerjoin(Station, Measurement.station == Station.station).group_by(Measurement.station)\
                .filter(Measurement.date >= start).filter(Measurement.date <= end).all()  
    range_stats = list(np.ravel(results))
    session.close()
    print()
    print("Temperature Statistics")
    return jsonify(range_stats) 

app.run(debug=True)