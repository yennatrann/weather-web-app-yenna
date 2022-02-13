# Framework: Flask
# Description: Create a weather web app with a dashboard where users can enter the name of a city and do a search by clicking a button. I used OpenWeatherApp API with Python request to get the data and return the current weather in that city in the dashboard.
# OpenWeatherApp Website: https://openweathermap.org/
# Open web app: https://weather-web-app-yenna.herokuapp.com/
# Github: https://github.com/yennatrann/weather-web-app-yenna

import requests
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecret'

db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=imperial&appid=2e7ca4dfd9bd9411a1e050549bb37004'

    # Get the response:
    r = requests.get(url).json()
    return r


@app.route('/')
def index_get():
    cities = City.query.all()

    # Create a list to hold the weather for all cities:
    weather_data = []

    for city in cities:
        r = get_weather_data(city.name)
        print(r)

        # Create a dictionary to store all data return from the response:
        weather = {
            'city': city.name,
            'temperature': r['main']['temp'],
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon'],
        }

        weather_data.append(weather)

    return render_template('weather.html', weather_data=weather_data)


@app.route('/', methods=['POST'])
def index_post():
    err_msg = ''
    new_city = request.form.get('city')

    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()

        # Check if the city exists, if not proceed to add city:
        if not existing_city:
            # Check if city is valid city:
            check_city_valid = get_weather_data(new_city)

            if check_city_valid['cod'] == 200:
                new_city_obj = City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                err_msg = 'Sorry, this city does not exist in the map.'

        else:
            err_msg = 'Sorry, this city is already added.'

    # Flash message from the previous call round:
    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('City is added successfully!')

    return redirect(url_for('index_get'))


@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()

    flash(f'{ city.name } is deleted!', 'success')
    return redirect(url_for('index_get'))


if __name__ == '__main__':
    app.run(debug=True)
