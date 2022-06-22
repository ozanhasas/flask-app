import pymongo
from flask import Flask, request, jsonify, make_response
from configparser import ConfigParser
from bson.objectid import ObjectId
import datetime
from flask_cors import CORS
import bson.json_util as json_util

app = Flask(__name__)
CORS(app)
config = ConfigParser()
config.read('app.cfg')
host = config['HOST']['host']
port = config['HOST']['port']
username = config['CREDENTIALS']['username']
password = config['CREDENTIALS']['password']

client = pymongo.MongoClient("mongodb+srv://"+username+":"+password+"@cluster0.fnvrd.mongodb.net/?retryWrites=true&w=majority")
mydb = client["Airbnb"]
house_collection = mydb["Home"]
reservation_collection = mydb["Reservation"]


@app.route('/getHousesByDate')
def getDateHouses():
    input_json = request.get_json()
    start_date_input = input_json['start_date']
    end_date_input = input_json['end_date']
    start_date = datetime.datetime(start_date_input['year'], start_date_input['month'], start_date_input['day'])
    end_date = datetime.datetime(end_date_input['year'], end_date_input['month'], end_date_input['day'])
    houses = house_collection.find()
    houses_id_list = []
    reservation_list = []
    for i in houses:
        houses_id_list.append(i['_id'])
    reservations = reservation_collection.find()
    for i in reservations:
        reservation_list.append(i)
    for id in houses_id_list:
        for res in reservation_list:
            if res['home_id'] == '':
                continue
            res_home_id = ObjectId(res['home_id'])
            res_start_date = res['start-date']
            res_end_date = res['end-date']
            if id == res_home_id:
                if (res_end_date > start_date >= res_start_date) or (res_end_date >= end_date > res_start_date) or ((start_date <= res_start_date) and (end_date >= res_end_date)):
                    houses_id_list.remove(id)
    selected_houses = house_collection.find({"_id": {"$in": houses_id_list}})
    house_list_new = []
    for i in selected_houses:
        house_list_new.append(i)
    output_json = json_util.dumps(house_list_new)
    return output_json


@app.route('/getHousesByDate2')
def getDateHouses2():
    input_json = request.get_json()
    start_date_input = input_json['start_date']
    end_date_input = input_json['end_date']
    start_date = datetime.datetime(start_date_input['year'], start_date_input['month'], start_date_input['day'])
    end_date = datetime.datetime(end_date_input['year'], end_date_input['month'], end_date_input['day'])
    house_list = []
    reservations = reservation_collection.find()
    removed_list = []
    for res in reservations:
        if res['home_id'] == '':
            continue
        res_home_id = ObjectId(res['home_id'])
        res_start_date = res['start-date']
        res_end_date = res['end-date']
        if not((start_date >= res_end_date) or (res_start_date >= end_date)):
            removed_list.append(res_home_id)
    selected_houses = house_collection.find({"_id": {"$nin": removed_list}})
    for i in selected_houses:
        house_list.append(i)
    output_json = json_util.dumps(house_list, ensure_ascii=False)
    return output_json


@app.route('/getHousesByDate3', methods=['GET', 'POST'])
def getDateHouses3():
    if request.mimetype != 'application/json':
        args = request.args
        start_date = datetime.datetime(int(args.get('syear')), int(args.get('smonth')), int(args.get('sday')))
        end_date = datetime.datetime(int(args.get('eyear')), int(args.get('emonth')), int(args.get('eday')))
    else:
        input_json = request.get_json()
        start_date_input = input_json['start_date']
        end_date_input = input_json['end_date']
        start_date = datetime.datetime(start_date_input['year'], start_date_input['month'], start_date_input['day'])
        end_date = datetime.datetime(end_date_input['year'], end_date_input['month'], end_date_input['day'])
    house_list = []
    reservations = reservation_collection.find()
    removed_list = []
    for res in reservations:
        if res['home_id'] == '':
            continue
        res_home_id = ObjectId(res['home_id'])
        res_start_date = res['start-date']
        res_end_date = res['end-date']
        if not((start_date >= res_end_date) or (res_start_date >= end_date)):
            removed_list.append(res_home_id)
    selected_houses = house_collection.find({"_id": {"$nin": removed_list}})
    for i in selected_houses:
        house_list.append(i)
    output_json = json_util.dumps(house_list, ensure_ascii=False)
    return output_json


@app.route('/getHousesByDesc', methods=['POST'])
def getHousesByDesc():

    input_json = request.get_json()
    keyword = input_json['keyword']
    search_list = [{"desc": {"$regex": ".*" + keyword + ".*"}}]
    houses = house_collection.find({"$or": search_list})
    houses_list = []
    for i in houses:
        houses_list.append(i)
    output_json = json_util.dumps(houses_list)
    return output_json


@app.route('/getHousesByTitle')
def getHousesByTitle():

    input_json = request.get_json()
    keyword = input_json['keyword']
    search_list = [{"title": {"$regex": ".*" + keyword + ".*"}}]
    houses = house_collection.find({"$or": search_list})
    houses_list = []
    for i in houses:
        houses_list.append(i)
    output_json = json_util.dumps(houses_list)
    return output_json


@app.route('/getHousesByCity')
def getHousesByCity():
    input_json = request.get_json()
    keyword = input_json['keyword']
    search_list = [{"sehir": {"$regex": ".*" + keyword + ".*"}}]
    houses = house_collection.find({"$or": search_list})
    houses_list = []
    for i in houses:
        houses_list.append(i)
    output_json = json_util.dumps(houses_list)
    return output_json


@app.route('/gethouses', methods=['POST'])
def gethouses():

    input_json = request.get_json()
    keyword = input_json['keyword']
    search_list = [{"desc": {"$regex": ".*"+keyword+".*"}}, {"title": {"$regex": ".*"+keyword+".*"}}, {"sehir": {"$regex": ".*"+keyword+".*"}}]
    houses = house_collection.find({"$or": search_list})
    houses_list = []
    for i in houses:
        houses_list.append(i)

    output_json = json_util.dumps(houses_list)


    return make_response(output_json, 200)



if __name__ == "__main__":
    app.run(host=host, port=int(port), debug=True)