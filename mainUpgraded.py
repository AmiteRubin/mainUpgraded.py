from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
from datetime import datetime
import os
from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session security
this_year = datetime.today().strftime('%y')
flight_data_file_path = os.path.join(os.getcwd(), f'Flight_Data_demo_1_{this_year}.csv')
operators_file_path = os.path.join(os.getcwd(), f'operators_demo_1_{this_year}.csv')
teams_file_path = os.path.join(os.getcwd(), f'teams_demo_1_{this_year}.csv')

google_client_id = "352166391876-0l55a5neb73p1ij1ae9frqumqqfdk2j3.apps.googleusercontent.com"

def verify_google_token(token):
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), google_client_id)

        # Extract relevant user information from idinfo
        user_info = {
            'sub': idinfo['sub'],
            'name': idinfo['name'],
            'email': idinfo['email'],
            # Additional information...
        }

        return user_info
    except ValueError:
        # Invalid token
        return None



if os.path.exists(flight_data_file_path):
    df_flight_data = pd.read_csv(flight_data_file_path, index_col='Flight Number')
else:
    #there is a need to include delta which is air_time
    df_flight_data = pd.DataFrame(columns=['Team', 'Location', 'Mission Purpose', 'Takeoff Time',\
                               'Landing Time', 'Air Time', 'Central Wing', 'Left Dihedral', 'Right Dihedral',\
                               'Boom Tail', 'Boom Engine', 'Height Rudder','Battery',\
                               'GPS Transmitter', 'Payload', 'Pod', 'Operator 1', 'Operator 2', 'Operator 3',\
                                'Operator 4', 'Exceptional Event Occurred', 'Exceptional Event Details',\
                                'Products' , 'Date Reported'])
    df_flight_data.index.name = 'Flight Number'
    df_flight_data.to_csv(flight_data_file_path)

if os.path.exists(operators_file_path):
    op_df = pd.read_csv(operators_file_path)
else:
    op_df = pd.DataFrame(columns=['Operator'],)
    op_df.to_csv(operators_file_path, index=False)

if os.path.exists(teams_file_path):
    teams_df = pd.read_csv(teams_file_path)
else:
    teams_df = pd.DataFrame(columns=['Team'],)
    teams_df.to_csv(teams_file_path, index=False)

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
        if 'google_id_token' in request.form:
            # Google Sign-In
            google_id_token = request.form['google_id_token']
            user_info = verify_google_token(google_id_token)

            if user_info:
                # Set the username in the session
                session['username'] = user_info.get('email', 'Google User')
                return redirect(url_for('index'))
            else:
                return render_template('login.html', message='Google Sign-In failed.')

        else:
            # Traditional login
            username = request.form['username']
            password = request.form['password']

            if username == hardcoded_user['username'] and password == hardcoded_user['password']:
                session['username'] = username  # Set the username in the session
                return redirect(url_for('index'))
            else:
                return render_template('login.html', message='Invalid username or password')

    return render_template('login.html', message='')

    return render_template('login.html', message='')

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the username from the session
    return redirect(url_for('index'))

@app.route('/report_flight', methods=['GET', 'POST'])
def report_flight():
    teams_list = pd.read_csv(teams_file_path)['Team'].tolist()
    operators_list = pd.read_csv(operators_file_path)['Operator'].tolist()
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Generate a new Flight Number as the next available index in the DataFrame
        flight_number = int(df_flight_data.index.max()) + 1 if not df_flight_data.empty else 1
        #flight_number = str(int(df.index.max()) + 1) if not df.empty else '1'
        team_name = request.form['team']
        location = request.form['location']
        mission_purpose = request.form['mission_purpose']
        takeoff_time = request.form['takeoff_time']
        landing_time = request.form['landing_time']
        takeoff_time_to_calc = datetime.strptime(request.form['takeoff_time'], '%Y-%m-%dT%H:%M')
        landing_time_to_calc = datetime.strptime(request.form['landing_time'], '%Y-%m-%dT%H:%M')

        # Calculate Air Time as timedelta
        air_time = landing_time_to_calc - takeoff_time_to_calc

        central_wing = request.form['central_wing']
        left_dihedral = request.form['left_dihedral']
        right_dihedral = request.form['right_dihedral']
        boom_tail = request.form['boom_tail']
        boom_engine = request.form['boom_engine']
        height_rudder = request.form['height_rudder']
        battery = request.form['battery']
        gps_transmitter = request.form['gps_transmitter']
        payload = request.form['payload']
        pod = request.form['pod']
        first_operator = request.form['first_operator']
        second_operator = request.form['second_operator']
        third_operator = request.form['third_operator']
        fourth_operator = request.form['fourth_operator']
        exceptional_event_bool = request.form.get('exceptional_event_bool') == 'True'
        exceptional_event_details = request.form['exceptional_event_details']
        products_bool = request.form.get('products_bool') == 'True'

        # Update DataFrame with new flight data including Air Time
        df_flight_data.loc[flight_number] = {
            'Team': team_name,
            'Location': location,
            'Mission Purpose': mission_purpose,
            'Takeoff Time': takeoff_time,
            'Landing Time': landing_time,
            'Air Time': air_time,
            'Central Wing': central_wing,
            'Left Dihedral': left_dihedral,
            'Right Dihedral': right_dihedral,
            'Boom Tail': boom_tail,
            'Boom Engine': boom_engine,
            'Height Rudder': height_rudder,
            'Battery': battery,
            'GPS Transmitter': gps_transmitter,
            'Payload': payload,
            'Pod': pod,
            'Operator 1': first_operator,
            'Operator 2': second_operator,
            'Operator 3': third_operator,
            'Operator 4': fourth_operator,
            'Exceptional Event Occurred': exceptional_event_bool,
            'Exceptional Event Details': exceptional_event_details,
            'Products': products_bool,
            'Date Reported': datetime.today().strftime('%d.%m.%y')
        }

        # Save DataFrame to CSV
        df_flight_data.to_csv(flight_data_file_path)

        flash(f"Flight report recorded successfully!")
        return render_template('index.html', username=session.get('username'))
        # Assuming 'index.html' is your landing page template

    return render_template('report_flight.html',\
                           username=session.get('username'), teams_list=teams_list,\
                           operators_list=operators_list)


@app.route('/report_takeoff', methods=['GET', 'POST'])
def report_takeoff():
    teams_list = pd.read_csv(teams_file_path)['Team'].tolist()
    operators_list = pd.read_csv(operators_file_path)['Operator'].tolist()
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Generate a new Flight Number as the next available index in the DataFrame
        # i think there is a need to convert flight_number to be an integer, and make it a string while
        # returned to a user. should check it out, and then .max() func won't do any problems of comparing
        # integers to strings.
        #flight_number = str(int(df.index.max()) + 1) if not df.empty else '1'
        flight_number = int(df_flight_data.index.max()) + 1 if not df_flight_data.empty else 1
        team_name = request.form['team']
        location = request.form['location']
        mission_purpose = request.form['mission_purpose']
        #there is a chance that there is no need to make it in that format. important for the users to
        #be able to read the time of takeoff and time of landing properly.
        takeoff_time = request.form['takeoff_time']
        central_wing = request.form['central_wing']
        left_dihedral = request.form['left_dihedral']
        right_dihedral = request.form['right_dihedral']
        boom_tail = request.form['boom_tail']
        boom_engine = request.form['boom_engine']
        height_rudder = request.form['height_rudder']
        battery = request.form['battery']
        gps_transmitter = request.form['gps_transmitter']
        payload = request.form['payload']
        pod = request.form['pod']
        first_operator = request.form['first_operator']
        second_operator = request.form['second_operator']
        third_operator = request.form['third_operator']
        fourth_operator = request.form['fourth_operator']

        #maybe use the index of the flight_number, rather then the string that represents it. it'll solve
        #the problem
        df_flight_data.loc[flight_number] = {
            'Team': team_name,
            'Location': location,
            'Mission Purpose': mission_purpose,
            'Takeoff Time': takeoff_time,
            'Central Wing': central_wing,
            'Left Dihedral': left_dihedral,
            'Right Dihedral': right_dihedral,
            'Boom Tail': boom_tail,
            'Boom Engine': boom_engine,
            'Height Rudder': height_rudder,
            'Battery': battery,
            'GPS Transmitter': gps_transmitter,
            'Payload': payload,
            'Pod': pod,
            'Operator 1': first_operator,
            'Operator 2': second_operator,
            'Operator 3': third_operator,
            'Operator 4': fourth_operator,
            #there is a need to understand, which time is considered to be the time of the report
            'Date Reported': datetime.today().strftime('%d.%m.%y')
        }

        # Save DataFrame to CSV
        df_flight_data.to_csv(flight_data_file_path)
        flash(f"Takeoff report recorded successfully, your flight number is {flight_number}!")
        return render_template('index.html', username=session.get('username'))

    return render_template('report_takeoff.html',username=session.get('username'),\
                           teams_list=teams_list, operators_list=operators_list)



@app.route('/report_landing', methods=['GET', 'POST'])
def report_landing():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Extract data from the form
        flight_number = request.form['flight_number']
        landing_time = request.form['landing_time']
        landing_time_to_calc = datetime.strptime(request.form['landing_time'], '%Y-%m-%dT%H:%M')
        exceptional_event_bool = request.form.get('exceptional_event_bool') == 'True'
        exceptional_event_details = request.form['exceptional_event_details']
        products_bool = request.form.get('products_bool') == 'True'

        # Locate the existing row in the DataFrame
        existing_row_index = df_flight_data.index.get_loc(int(flight_number))

        # Extract takeoff time from the existing row
        takeoff_time_to_calc = datetime.strptime(\
            df_flight_data.loc[df_flight_data.index[existing_row_index]]['Takeoff Time'],'%Y-%m-%dT%H:%M')

        # Calculate Air Time as timedelta
        air_time = landing_time_to_calc - takeoff_time_to_calc

        # Update the entire row in the DataFrame
        df_flight_data.loc[df_flight_data.index[existing_row_index], 'Landing Time'] = landing_time
        df_flight_data.loc[df_flight_data.index[existing_row_index], 'Air Time'] = air_time
        df_flight_data.loc[df_flight_data.index[existing_row_index], 'Exceptional Event Occurred'] =\
            exceptional_event_bool
        df_flight_data.loc[df_flight_data.index[existing_row_index], 'Exceptional Event Details'] =\
            exceptional_event_details
        df_flight_data.loc[df_flight_data.index[existing_row_index], 'Products'] = products_bool

        # Save DataFrame to CSV
        df_flight_data.to_csv(flight_data_file_path)

        flash(f"Landing report recorded successfully!")
        return redirect(url_for('index'))

    return render_template('report_landing.html', username=session.get('username'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Extract rows without 'Landing Time'
    on_air_df = df_flight_data[df_flight_data['Landing Time'].isna()]

    # Calculate the current time
    current_time = datetime.today()

    # Calculate the current air time for each flight - reformat to amount of hours : amount of minutes
    on_air_df['Current Air Time'] = current_time - pd.to_datetime(on_air_df['Takeoff Time'])

    # Convert the time difference to hours and minutes
    on_air_df['Current Air Time'] = on_air_df['Current Air Time'].apply(\
        lambda x: "{:0>2}:{:0>2}".format(int(x.total_seconds() // 3600), int((x.total_seconds() % 3600) // 60)))

    # Reset the index to include 'Flight Number' as a regular column
    on_air_df = on_air_df.reset_index()

    # Select relevant columns for the table
    on_air_table_columns = ['Flight Number', 'Team', 'Location', 'Takeoff Time', 'Current Air Time']

    # Convert DataFrame to list of dictionaries for rendering in the template
    on_air_table_data = on_air_df[on_air_table_columns].to_dict(orient='records')

    exc_event_df = df_flight_data[df_flight_data['Exceptional Event Occurred'] == True]

    exc_event_df = exc_event_df.reset_index()

    exc_event_df_table_columns = ['Flight Number', 'Team', 'Location',\
                                  'Exceptional Event Details', 'Air Time', 'Date Reported']

    # Convert DataFrame to list of dictionaries for rendering in the template
    exc_event_table_data = exc_event_df[exc_event_df_table_columns]#.to_dict(orient='records')

    return render_template('dashboard.html', on_air_table_data=on_air_table_data,\
                           on_air_table_columns=on_air_table_columns,\
                           exc_event_table_data=exc_event_table_data, \
                           exc_event_df_table_columns=exc_event_df_table_columns,\
                           username=session.get('username'))

"""
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Load CSV data
    df_flight_data = pd.read_csv(csv_file_path)  # Replace 'your_csv_file.csv' with your actual CSV file path

    # Check the data types of the columns
    print(df_flight_data.dtypes)

    # Ensure 'Exceptional Event Occurred' column is boolean
    if df_flight_data['Exceptional Event Occurred'].dtype != bool:
        raise ValueError("The 'Exceptional Event Occurred' column is not of boolean type.")

    # Extract rows without 'Landing Time'
    on_air_df = df_flight_data[df_flight_data['Landing Time'].isna()]

    # Calculate the current time
    current_time = datetime.today()

    # Calculate the current air time for each flight - reformat to amount of hours : amount of minutes
    on_air_df['Current Air Time'] = current_time - pd.to_datetime(on_air_df['Takeoff Time'])

    # Convert the time difference to hours and minutes
    on_air_df['Current Air Time'] = on_air_df['Current Air Time'].apply(
        lambda x: "{:0>2}:{:0>2}".format(int(x.total_seconds() // 3600), int((x.total_seconds() % 3600) // 60)))

    # Reset the index to include 'Flight Number' as a regular column
    on_air_df = on_air_df.reset_index()

    # Select relevant columns for the table
    on_air_table_columns = ['Flight Number', 'Team', 'Location', 'Takeoff Time', 'Current Air Time']

    # Convert DataFrame to list of dictionaries for rendering in the template
    on_air_table_data = on_air_df[on_air_table_columns].to_dict(orient='records')

    # Filter DataFrame for exceptional events
    exc_event_df = df_flight_data[df_flight_data['Exceptional Event Occurred'] == True]

    # Check if there are any exceptional events present
    if not exc_event_df.empty:
        exc_event_df = exc_event_df.reset_index()

        exc_event_df_table_columns = ['Flight Number', 'Team', 'Location',
                                      'Exceptional Event Details', 'Air Time', 'Date Reported']

        # Convert DataFrame to list of dictionaries for rendering in the template
        exc_event_table_data = exc_event_df[exc_event_df_table_columns]
    else:
        exc_event_table_data = None
        exc_event_df_table_columns = None

    return render_template('dashboard.html', on_air_table_data=on_air_table_data,
                           on_air_table_columns=on_air_table_columns,
                           exc_event_table_data=exc_event_table_data,
                           exc_event_df_table_columns=exc_event_df_table_columns,
                           username=session.get('username'))

"""
"""
@app.route('/statistics')
def statistics():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Extract rows without 'Landing Time'
    on_air_df = df[df['Landing Time'].isna()]

    # Reset the index to include 'Flight Number' as a regular column
    on_air_df = on_air_df.reset_index()

    # Select relevant columns for the table
    on_air_table_columns = ['Flight Number', 'Team', 'Location', 'Takeoff Time']

    exc_event_df = df[df['Exceptional Event Occurred'] == True]

    exc_event_df = exc_event_df.reset_index()

    exc_event_df_table_columns = ['Flight Number', 'Team', 'Location', 'Exceptional Event Details',\
                                  'Date Reported']

    # Convert DataFrame to list of dictionaries for rendering in the template
    on_air_table_data = on_air_df[on_air_table_columns].to_dict(orient='records')

    exc_event_table_data = exc_event_df[exc_event_df_table_columns]


    # Get coordinates of teams that haven't landed
    team_coordinates = on_air_df[['Team', 'Location']].dropna()

    # Convert coordinates to a list of dictionaries
    coordinates_list = team_coordinates.to_dict(orient='records')
    return render_template('dashboard.html', on_air_table_data=on_air_table_data,\
                           on_air_table_columns=on_air_table_columns,\
                           exc_event_table_data=exc_event_table_data, \
                           exc_event_df_table_columns=exc_event_df_table_columns,\
                           username=session.get('username'))
"""



@app.route('/manage_manpower', methods=['GET', 'POST'])
def manage_manpower():
    if 'username' not in session:
        return redirect(url_for('login'))

    op_columns = ['Operator']
    team_columns = ['Team']

    # Load the existing operator and team DataFrames from CSV
    op_df = pd.read_csv(operators_file_path)
    teams_df = pd.read_csv(teams_file_path)

    if request.method == 'POST':
        op_add_bool = request.form.get('op_add_bool') == 'True'
        team_add_bool = request.form.get('team_add_bool') == 'True'
        op_erase_bool = request.form.get('op_erase_bool') == 'True'
        team_erase_bool = request.form.get('team_erase_bool') == 'True'

        if op_add_bool:
            op_to_add = request.form['op_to_add']
            op_list_to_add = op_to_add.split(',')
            for operator in op_list_to_add:
                if operator not in op_df['Operator'].tolist():
                    op_df = op_df.append({'Operator': operator}, ignore_index=True)

        if team_add_bool:
            teams_to_add = request.form['teams_to_add']
            teams_list_to_add = teams_to_add.split(',')
            for team in teams_list_to_add:
                if team not in teams_df['Team'].tolist():
                    teams_df = teams_df.append({'Team': team}, ignore_index=True)

        if op_erase_bool:
            op_to_erase = request.form['op_to_erase']
            op_list_to_erase = op_to_erase.split(',')
            op_df = op_df[~op_df['Operator'].isin(op_list_to_erase)]
        #strip spaces
        if team_erase_bool:
            teams_to_erase = request.form['teams_to_erase']
            teams_list_to_erase = teams_to_erase.split(',')
            teams_df = teams_df[~teams_df['Team'].isin(teams_list_to_erase)]

        # Sort the DataFrames by Operator and Team columns
        op_df.sort_values(by=['Operator'], inplace=True)
        teams_df.sort_values(by=['Team'], inplace=True)

        # Save the updated DataFrames to CSV
        op_df.to_csv(operators_file_path, index=False)
        teams_df.to_csv(teams_file_path, index=False)

        flash("Operators and Teams were added/erased successfully!")

    return render_template('manage_manpower.html', op_df=op_df,
                           team_df=teams_df,
                           op_columns=op_columns,
                           team_columns=team_columns,
                           username=session.get('username'))

#todo complete the manage equipment template
"""
@app.route('/manage_equipment', methods=['GET', 'POST'])
def manage_equipment():
    # there is a need to include a file that handles the current flights of team, on going.
    # due to current situation, there is no need to handle more than one flight at a time
    if 'username' not in session:
        return redirect(url_for('login'))
    team_name = session['username'] # strip the team from username, and create a folder accordingly
    team_equipment_file_path = os.path.join(os.getcwd(),f'teams\\{team_name}')

    if os.path.exists(team_equipment_file_path):
        team_equipment_df = pd.read_csv(team_equipment_file_path)
    else:
        team_equipment_df = pd.DataFrame(columns=['Central Wing', 'Left Dihedral', 'Right Dihedral',\
                               'Boom Tail', 'Boom Engine', 'Height Rudder','Battery',\
                               'GPS Transmitter', 'Payload', 'Pod'], )
        team_equipment_df.to_csv(team_equipment_file_path, index=False)
    # call a function to initiate the first table for the team, with the zeros in the relevant elements
    # if a part is missing, insert ID 0, 00, 000, 0000, 00000 in order to distinct between them
    if request.method == 'POST':
        change_parts_bool = request.form.get('change_parts_bool') == 'True'
        if change_parts_bool:
            central_wing_replace_bool = request.form.get('central_wing_replace_bool') == 'True'
            right_dihedral_replace_bool = request.form.get('right_dihedral_replace_bool') == 'True'
            left_dihedral_replace_bool = request.form.get('left_dihedral_replace_bool') == 'True'
            boom_tail_replace_bool = request.form.get('boom_tail_replace_bool') == 'True'
            boom_engine_replace_bool = request.form.get('boom_engine_replace_bool') == 'True'
            height_rudder_replace_bool = request.form.get('height_rudder_replace_bool') == 'True'
            battery_replace_bool = request.form.get('battery_replace_bool') == 'True'
            gps_transmitter_replace_bool = request.form.get('gps_transmitter_replace_bool') == 'True'
            payload_replace_bool = request.form.get('payload_replace_bool') == 'True'
            pod_replace_bool = request.form.get('pod_replace_bool') == 'True'







        if op_add_bool:
            op_to_add = request.form['op_to_add']
            op_list_to_add = op_to_add.split(',')
            for operator in op_list_to_add:
                if operator not in op_df['Operator'].tolist():
                    op_df = op_df.append({'Operator': operator}, ignore_index=True)

        if team_add_bool:
            teams_to_add = request.form['teams_to_add']
            teams_list_to_add = teams_to_add.split(',')
            for team in teams_list_to_add:
                if team not in teams_df['Team'].tolist():
                    teams_df = teams_df.append({'Team': team}, ignore_index=True)

        if op_erase_bool:
            op_to_erase = request.form['op_to_erase']
            op_list_to_erase = op_to_erase.split(',')
            op_df = op_df[~op_df['Operator'].isin(op_list_to_erase)]
        #strip spaces
        if team_erase_bool:
            teams_to_erase = request.form['teams_to_erase']
            teams_list_to_erase = teams_to_erase.split(',')
            teams_df = teams_df[~teams_df['Team'].isin(teams_list_to_erase)]

        # Sort the DataFrames by Operator and Team columns
        op_df.sort_values(by=['Operator'], inplace=True)
        teams_df.sort_values(by=['Team'], inplace=True)

        # Save the updated DataFrames to CSV
        op_df.to_csv(operators_file_path, index=False)
        teams_df.to_csv(teams_file_path, index=False)

        flash("Operators and Teams were added/erased successfully!")

    return render_template('manage_manpower.html', op_df=op_df,
                           team_df=teams_df,
                           op_columns=op_columns,
                           team_columns=team_columns,
                           username=session.get('username'))
"""

if __name__ == '__main__':
    app.run(debug=True)#host='IPv4', port = 5000 remember to turnoff firewall
