import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.pool import SingletonThreadPool

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread':False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&#60YYYY-MM-DD&#62<br/>"
        f"/api/v1.0/&#60YYYY-MM-DD&#62/&#60YYYY-MM-DD&#62"
    )


@app.route("/api/v1.0/precipitation")
def rain():
    """Return a list showing the history of precipitation in Hawaii"""
    # Query all dates and precipitations in measurement
    rain_results = session.query(Measurement).all()

    # Convert the results to a dictionary
    rainfall = []
    for rf_row in rain_results:
        rain_dict = {}
        rain_dict[rf_row.date] = rf_row.prcp
        rainfall.append(rain_dict)

    # Return as a JSON
    return jsonify(rainfall)


@app.route("/api/v1.0/stations")
def Stations():
    """Return a list of stations including its id, name, latitude, longitude and elevation"""
    # Query all stations
    stat_results = session.query(Station).all()

    # Create a dictionary from the row data and append to a list of stations
    stats = []
    for st_row in stat_results:
        station_dict = {}
        station_dict["station_id"] = st_row.station
        station_dict["name"] = st_row.name
        station_dict["latitude"] = st_row.latitude
        station_dict["longitude"] = st_row.longitude
        station_dict["elevation"] = st_row.elevation
        stats.append(station_dict)

    return jsonify(stats)

@app.route("/api/v1.0/tobs")
def obsvTemp():
    """Return a list showing the history of observed temperatures in Hawaii"""
    # Find the last date in the database
    last = session.query(Measurement).order_by(Measurement.date.desc()).first()
    target_date = dt.datetime.strptime(last.date, '%Y-%m-%d') - dt.timedelta(days=365)
    # Query the last year's worth of measurements
    results = session.query(Measurement).filter(Measurement.date > target_date).order_by(Measurement.date)

    # Convert the results to a dictionary
    tobs = []
    for row in results:
        tobs_dict = {}
        tobs_dict[row.date] = row.tobs
        tobs.append(tobs_dict)

    # Return as a JSON
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def afterSumm(start):
    """Return a list showing the lowest, highest and average of observed temperatures in Hawaii after the specified date"""
    # Strip the date from the input
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    # Query the last year's worth of measurements
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    lo, av, hi = session.query(*sel).filter(Measurement.date >= start_date).all()[0]

    # Convert the results to a dictionary
    lah_dict = {}
    lah_dict["low"] = lo
    lah_dict["average"] = av
    lah_dict["high"] = hi

    # Return as a JSON
    return jsonify([lah_dict])

@app.route("/api/v1.0/<start>/<end>")
def rangeSumm(start, end):
    """Return a list showing the lowest, highest and average of observed temperatures in Hawaii between the specified dates"""
    # Strip the date from the input
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    stop_date = dt.datetime.strptime(end, '%Y-%m-%d')
    if(stop_date < start_date):
        temp = stop_date
        stop_date = start_date
        start_date = temp
    # Query the last year's worth of measurements
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    lo, av, hi = session.query(*sel).filter(Measurement.date >= start_date).filter(Measurement.date <= stop_date).all()[0]

    # Convert the results to a dictionary
    lah_dict = {}
    lah_dict["low"] = lo
    lah_dict["average"] = av
    lah_dict["high"] = hi

    # Return as a JSON
    return jsonify([lah_dict])

if __name__ == '__main__':
    app.run(debug=True)
