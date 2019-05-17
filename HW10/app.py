import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import pandas as pd
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
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
    # Home page.
    # List all routes that are available.
    return (
        f"Available Routes:<br/>"
        f"/api/precipitation<br/>"
        f"/api/stations<br/>"
        f"/api/temperature<br/>"
        f"/api/<start><br/>"
        f"/api/<start>/<end>"
    )


@app.route("/api/precipitation")
def precipitation():
    # Convert the query results to a Dictionary using date as the key and prcp as the value.
    # Return the JSON representation of your dictionary.
 
    # Query all results
    sel = [Measurement.date, Measurement.prcp]
 
    results = session.query(*sel).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of all_prcp
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)


@app.route("/api/stations")
def stations():
    # Return a JSON list of stations from the dataset.

    # Query all stations
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/temperature")
def temperature():
    # Query for the dates and temperature observations from a year from the last data point.
    # Return a JSON list of Temperature Observations (tobs) for the previous year.
 
    # Query results
    sel = [Measurement.date, Measurement.tobs]

    results = session.query(*sel).\
        filter(Measurement.date >= '2016-08-23').\
        filter(Measurement.date <= '2017-08-23').\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()

    # Convert list of tuples into normal list
    all_temps = list(np.ravel(results))

    return jsonify(all_temps)


@app.route("/api/<start>")
def start(start_date):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or 
    # start-end range.
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date. 

    # Query results 
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    # Convert list of tuples into normal list
    start_list = list(np.ravel(results))

    return jsonify(start_list)


@app.route("/api/<start>/<end>")
def end(start_date, end_date):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or 
    # start-end range.
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

    # Query results
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Convert list of tuples into normal list
    start_end = list(np.ravel(results))

    return jsonify(start_end)


if __name__ == '__main__':
    app.run(debug=True)