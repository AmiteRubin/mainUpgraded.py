from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from datetime import datetime
import pandas as pd
import os

# Set a secret key for session security
SECRET_KEY = 'your_secret_key'

this_year = datetime.today().strftime('%y')
csv_file_path = os.path.join(os.getcwd(), f'Flight_Data_{this_year}.csv')

if os.path.exists(csv_file_path):
    df = pd.read_csv(csv_file_path, index_col='Flight Number')
else:
    df = pd.DataFrame(columns=['Team', 'Location', 'Mission Purpose', 'Takeoff Time', 'Landing Time', 'Date'])
    df.index.name = 'Flight Number'

# Hardcoded user for demonstration purposes
hardcoded_user = {
    'username': 'demo_user',
    'password': 'password123'
}

def index(request):
    return render(request, 'flights/index.html', {'username': request.session.get('username', '')})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if username == hardcoded_user['username'] and password == hardcoded_user['password']:
            request.session['username'] = username
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'flights/login.html', {'message': messages.get_messages(request)})

def logout(request):
    request.session.pop('username', None)
    return redirect('index')

def welcome(request):
    return HttpResponse('Welcome to the website!')

def report_flight(request):
    if 'username' not in request.session:
        return redirect('login')

    if request.method == 'POST':
        # Generate a new Flight Number as the next available index in the DataFrame
        flight_number = str(int(df.index.max()) + 1) if not df.empty else '1'
        team_name = request.POST['team']
        location = request.POST['location']
        mission_purpose = request.POST['mission_purpose']
        takeoff_time = request.POST['takeoff_time']
        landing_time = request.POST['landing_time']

        # Update DataFrame with new flight data
        df.loc[flight_number] = {
            'Team': team_name,
            'Location': location,
            'Mission Purpose': mission_purpose,
            'Takeoff Time': takeoff_time,
            'Landing Time': landing_time,
            'Date': datetime.today().strftime('%d.%m.%y')
        }

        # Save DataFrame to CSV
        df.to_csv(csv_file_path)

        messages.success(request, 'Flight reported successfully.')
        return redirect('index')

    return render(request, 'flights/report_flight.html')
