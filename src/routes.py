from datetime import datetime as dt

from flask import current_app as app
from flask import make_response, redirect, render_template, request, url_for

from sqlalchemy import func, text

from .models import db, Agency,Calendar, Calendar_dates, Routes, Shapes, Stop_times, Stops, Trips
from .utils import distance, date_to_str
from .const import HttpStatus
from datetime import datetime, date, time, timedelta

@app.route("/schedule", methods=["POST"])
def schedule():
    content = request.get_json()
    origin_station_id = content.get('origin_station_id')
    coordinates = content.get('coordinates')
    destination_station_id = content.get('destination_station_id')

    order = content.get('order')
    limit = content.get('limit')
    offset = content.get('offset')

    if not destination_station_id:
        return 'Destination station ID is required', HttpStatus.BAD_REQUEST
    elif not (coordinates or origin_station_id):
        return 'Coordinates or Origin Station ID is required', HttpStatus.BAD_REQUEST
    elif origin_station_id:
        origin_stop = Stops.query.filter_by(stop_id=origin_station_id).first()
        destination_stop = Stops.query.filter_by(stop_id=destination_station_id).first()
        distance_between_stops = distance(origin_stop.stop_lat, destination_stop.stop_lat, origin_stop.stop_lon, destination_stop.stop_lon)
        if distance_between_stops > 10:
            return 'Routes not available', HttpStatus.NOT_FOUND
    elif coordinates:
        cur_lat = float(coordinates['latitude'])
        cur_lon = float(coordinates['longitude'])
        all_stops = Stops.query.all()
        closest_stop = {'stop_id': "", 'distance': 4000}
        for stop in all_stops:
            distance_to_stop = distance(cur_lat, stop.stop_lat, cur_lon, stop.stop_lon)
            if closest_stop['distance'] > distance_to_stop:
                closest_stop['stop_id'] = stop.stop_id
                closest_stop['distance'] = distance_to_stop


        origin_station_id = closest_stop['stop_id']
        
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    weekday = days[datetime.today().weekday()]

    service_id = ''

    service_id_from_calendar = Calendar.query\
                    .filter(Calendar.__table__.c[weekday]==1).first()

    service_id = service_id_from_calendar.service_id

    check_holiday = Calendar_dates.query\
                    .filter_by(service_id=service_id_from_calendar.service_id)\
                    .filter_by(date=date_to_str(date.today()))\
                    .filter_by(exception_type=2).first()

    if check_holiday:
        service_id = check_holiday.service_id

    query_statement = text(f"select s.trip_id, r.route_short_name, \
        sum(case when stop_id = '{origin_station_id}' then 1 else 0 end) as origin_station,\
        max(case when stop_id = '{origin_station_id}' then s.stop_sequence else 0 end) as origin_station_sequence,\
        max(case when stop_id = '{origin_station_id}' then s.arrival_time else 0 end) as origin_arrival_time,\
        sum(case when stop_id = '{destination_station_id}' then 1 else 0 end) as destination_station,\
        max(case when stop_id = '{destination_station_id}' then s.stop_sequence else 0 end) as destination_station_sequence\
            from stop_times as s inner join trips as t on\
        s.trip_id = t.trip_id\
        inner join routes as r on\
        t.route_id = r.route_id\
        where s.stop_id in ('{origin_station_id}', '{destination_station_id}')\
        and t.service_id = '{service_id}'\
        and s.arrival_time > '{datetime.now().time()}'\
        group by s.trip_id, r.route_short_name \
        having origin_station = 1 and destination_station = 1 and origin_station_sequence != 0 and destination_station_sequence != 0\
            and max(case when stop_id = '{origin_station_id}' then stop_sequence else 0 end) < max(case when stop_id = '{destination_station_id}' then stop_sequence else 0 end)\
        order by max(case when stop_id = '{origin_station_id}' then arrival_time else 0 end) \
        ")

    result_json = {}
    next_schedules = []
    pagination = {}

    with db.engine.connect() as connection:
        result = connection.execute(query_statement).fetchall()

        if len(result) == 0:
            return 'Routes not available', HttpStatus.NOT_FOUND

        for row in result:
            delta_days = 0
            if int(row.origin_arrival_time[:2]) >= 24:
                stop_time = datetime.strptime(str(int(row.origin_arrival_time[:2])-24)+row.origin_arrival_time[2:], '%H:%M:%S').time()
                delta_days = 1
            else:
                stop_time = datetime.strptime(row.origin_arrival_time, '%H:%M:%S').time()
            next_schedules.append({'route_short_name': row.route_short_name, 'arrival_time': datetime.combine(date.today()+timedelta(days=delta_days), stop_time)})

    pagination['total'] = len(result)
    pagination['order'] = order if order is not None and order == 'desc' else 'asc'
    pagination['limit'] = limit if limit is not None and limit > 0 else 5
    pagination['offset'] = offset if offset is not None and offset > 0 else 0

    reverse = pagination['order'] == 'desc'

    next_schedules.sort(reverse=reverse, key=lambda x:x['arrival_time'])

    result_json['next_schedules'] = next_schedules[pagination['offset']:pagination['offset']+pagination['limit'] ]
    result_json['pagination'] = pagination

    return result_json, HttpStatus.OK