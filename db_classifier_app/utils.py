import json
import numpy as np
from scipy.optimize import curve_fit
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
import os
from . import views

def nonlinear_function(x, a, b, c, d):
    return a * np.exp(-b * x) + c * np.power(x, d)


def estimate_timings(rows, metrics, data_structure):
    data_points = [
        (
            int(key),
            float(value["insertion_avg"]),
            float(value[f"Q{data_structure}_avg"]),
        )
        for key, value in metrics.items()
        if key.isnumeric()  # Ensure the key is numeric
    ]
    if not data_points:
        return None
    data_points.sort(key=lambda x: x[0])

    x = np.array([point[0] for point in data_points])
    y_insertion = np.array([point[1] for point in data_points])
    y_query = np.array([point[2] for point in data_points])

    initial_guess = [1, 1, 1, 1]
    popt_insertion, _ = curve_fit(
        nonlinear_function, x, y_insertion, p0=initial_guess, maxfev=10000
    )

    popt_query, _ = curve_fit(
        nonlinear_function, x, y_query, p0=initial_guess, maxfev=10000
    )

    insertion_time = nonlinear_function(rows, *popt_insertion)
    query_time = nonlinear_function(rows, *popt_query)

    return {
        "insertion": max(0, insertion_time),
        f"Q{data_structure}": max(0, query_time),
    }


def recommend_database_v2(rows, data_structure, data_file):
    base_path = os.path.dirname(os.path.abspath(__file__))  # Get the current file's directory
    data_file_path = os.path.join(base_path, 'static',
                                  data_file)  # Join the base path with 'staticfiles' and the filename

    with open(data_file_path, "r") as file:
        database_data = json.load(file)

    results = []

    for db_name, db_data in database_data.items():
        try:
            timings = estimate_timings(rows, db_data, data_structure)  # Using the updated function
            if timings is None:  # Check if timings is None before trying to access its items
                continue
            insertion_time = timings["insertion"]
            query_time = timings[f"Q{data_structure}"]
            results.append((db_name, insertion_time, query_time))
        except Exception as e:
            print(f"Exception for {db_name}: {str(e)}")
            continue

    results.sort(key=lambda x: (x[1], x[2]))
    return results[:8]  # Return the top 8 databases based on insertion and query times
