from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from datetime import datetime
import os
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session security
this_year = datetime.today().strftime('%y')
csv_file_path = os.path.join(os.getcwd(), f'Flight_Data_{this_year}.csv')
if os.path.exists(csv_file_path):
    df = pd.read_csv(csv_file_path, index_col='Flight Number')
else:
    df = pd.DataFrame(columns=['Team', 'Location', 'Mission Purpose', 'Takeoff Time',\
                               'Landing Time','Central Wing', 'Left Dihedral', 'Right Dihedral',\
                               'Boom Tail', 'Boom Engine', 'Height Rudder','Battery',\
                               'GPS Transmitter', 'Exceptional Event Occurred', 'Exceptional Event Details',\
                                'Products' , 'Date Reported'])
    #to be added - Op1,Op2,Op3,Op4
    df.index.name = 'Flight Number'

# Hardcoded user for demonstration purposes
hardcoded_user = {
    'username': 'demo_user',
    'password': 'password123'
}

@app.route('/')
def index():
    return render_template('index.html', username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == hardcoded_user['username'] and password == hardcoded_user['password']:
            session['username'] = username  # Set the username in the session
            return redirect(url_for('index'))
        else:
            return render_template('login.html', message='Invalid username or password')

    return render_template('login.html', message='')

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the username from the session
    return redirect(url_for('index'))
"""
@app.route('/welcome')
def welcome():
    return 'Welcome to the website!'
    """

@app.route('/report_flight', methods=['GET', 'POST'])
def report_flight():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Generate a new Flight Number as the next available index in the DataFrame
        flight_number = str(int(df.index.max()) + 1) if not df.empty else '1'
        team_name = request.form['team']
        location = request.form['location']
        mission_purpose = request.form['mission_purpose']
        takeoff_time = request.form['takeoff_time']
        landing_time = request.form['landing_time']
        central_wing = request.form['central_wing']
        left_dihedral = request.form['left_dihedral']
        right_dihedral = request.form['right_dihedral']
        boom_tail = request.form['boom_tail']
        boom_engine = request.form['boom_engine']
        height_rudder = request.form['height_rudder']
        battery = request.form['battery']
        gps_transmitter = request.form['gps_transmitter']
        #exceptional_event_bool = request.form['exceptional_event_bool']
        exceptional_event_bool = request.form.get('exceptional_event_bool') == 'True'
        exceptional_event_details = request.form['exceptional_event_details']
        #products_bool = request.form['products_bool']
        products_bool = request.form.get('products_bool') == 'True'
        """
        exceptional_event_bool = request.form.get('exceptional_event_bool') == 'True'
        products_bool = request.form.get('products_bool') == 'True'

        """
        ##time_of_fligt = takeoff_time - landing_time <-- format of hour! take into consideration that
        ##time difference could be from two different days!
        # Update DataFrame with new flight data
        df.loc[flight_number] = {
            'Team': team_name,
            'Location': location,
            'Mission Purpose': mission_purpose,
            'Takeoff Time': takeoff_time,
            'Landing Time': landing_time,
            'Central Wing': central_wing,
            'Left Dihedral': left_dihedral,
            'Right Dihedral': right_dihedral,
            'Boom Tail': boom_tail,
            'Boom Engine': boom_engine,
            'Height Rudder': height_rudder,
            'Battery': battery,
            'GPS Transmitter': gps_transmitter,
            'Exceptional Event Occurred': exceptional_event_bool,
            'Exceptional Event Details': exceptional_event_details,
            'Products': products_bool,
            'Date Reported': datetime.today().strftime('%d.%m.%y')
        }

        # Save DataFrame to CSV
        df.to_csv(csv_file_path)
        #todo return message - "Success"
        return redirect(url_for('index'))

    return render_template('report_flight.html')

if __name__ == '__main__':
    app.run(debug=True)
