from models import *
from flask import Flask, request
from flask.json import jsonify
from flask_migrate import Migrate
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from datetime import date
from http import HTTPStatus

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.sqlite3'
app.config['SECRET_KEY'] = "secret key"
db.init_app(app)
Migrate(app, db)


@app.route('/')
def home():
    return "Hello"


@app.before_first_request
def setup_db():
    db.init_app(app)
    db.create_all()


@app.route('/create_user/<role>', methods=['POST'])
def create_user(role):
    data = request.json
    if role == 'patient':
        user = Patient(name=data.get('name'), hashed_pass=data.get('hashed_pass'), national_id=data.get('national_id'))

    else:
        user = Doctor(name=data.get('name'), hashed_pass=data.get('hashed_pass'), national_id=data.get('national_id'))

    try:
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'Successful'}), HTTPStatus.CREATED

    except IntegrityError as e:
        if 'UNIQUE' in str(e):
            return jsonify({'message': 'Error: national id is in use'}), HTTPStatus.CONFLICT


@app.route('/create_admin', methods=['POST'])
def create_admin():
    data = request.json

    user = Admin(username=data.get('username'), hashed_pass=data.get('hashed_pass'))

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'Successful'}), HTTPStatus.CREATED

    except IntegrityError as e:
        if 'UNIQUE' in str(e):
            return jsonify({'message': 'Error: username is in use'}), HTTPStatus.CONFLICT


@app.route('/user/<role>/<national_id>')
def get_user(role, national_id):
    if role == "patient":
        user = Patient.query.filter_by(national_id=national_id).first()
    else:
        user = Doctor.query.filter_by(national_id=national_id).first()

    if user is None:
        return jsonify({'message': 'Error: No user found'}), HTTPStatus.NOT_FOUND
    else:
        return jsonify({'message': 'Successful', 'user': user.to_dict()}), HTTPStatus.OK


@app.route('/admin/<username>')
def get_admin(username):
    user = Admin.query.get(username)

    if user is None:
        return jsonify({'message': 'Error: No user found'}), HTTPStatus.NOT_FOUND
    else:
        return jsonify({'message': 'Successful', 'user': user.to_dict()}), HTTPStatus.OK


@app.route("/user_profile")
def get_user_profile():
    data = request.args.to_dict(flat=False)
    username = data["username"][0]
    role = data["role"][0]
    if role == "patient":
        user = Patient.query.filter_by(national_id=username).first()
    else:
        user = Doctor.query.filter_by(national_id=username).first()

    keys = ['name', 'national_id']
    your_dict = {key: user.to_dict()[key] for key in keys}
    your_dict["role"] = role
    return jsonify({'message': 'Successful', 'user': your_dict}), HTTPStatus.OK


@app.route("/admin_profile")
def get_admin_profile():
    username = list(request.args.to_dict(flat=False).keys())[0]
    user = Admin.query.get(username)
    keys = ['username']
    your_dict = {key: user.to_dict()[key] for key in keys}

    return jsonify({'message': 'Successful', 'user': your_dict}), HTTPStatus.OK


@app.route('/show_patients/', methods=['GET'])
def patients():
    username = list(request.args.to_dict(flat=False).keys())[0]
    admin = Admin.query.get(username)
    if admin is None:
        return jsonify({'message': 'Error: you have not access'}), HTTPStatus.NOT_FOUND
    final_list = []
    keys = ['name', 'national_id']
    temp = [x.to_dict() for x in Patient.query.all()]
    for i in range(len(temp)):
        x = temp[i]
        your_dict = {key: x[key] for key in keys}
        final_list.append(your_dict)

    return jsonify(final_list)


@app.route('/show_doctors/', methods=['GET'])
def doctors():
    username = list(request.args.to_dict(flat=False).keys())[0]
    admin = Admin.query.get(username)
    if admin is None:
        return jsonify({'message': 'Error: you have not access'}), HTTPStatus.NOT_FOUND
    final_list = []
    keys = ['name', 'national_id']
    temp = [x.to_dict() for x in Doctor.query.all()]
    for i in range(len(temp)):
        x = temp[i]
        your_dict = {key: x[key] for key in keys}
        final_list.append(your_dict)

    return jsonify(final_list)


@app.route('/patients/stats', methods=['GET'])
def patients_stats():
    query = Patient.query
    try:
        day = int(request.args["day"])
        month = int(request.args["month"])
        year = int(request.args["year"])
        date_obj = date(year, month, day)
    except:
        return jsonify({"message": "Bad request"}), HTTPStatus.BAD_REQUEST
    query = query.filter(func.DATE(Patient.timestamp) == date_obj)
    return jsonify([patient.to_dict() for patient in query.all()])


@app.route('/doctors/stats', methods=['GET'])
def doctors_stats():
    query = Doctor.query
    try:
        day = int(request.args["day"])
        month = int(request.args["month"])
        year = int(request.args["year"])
        date_obj = date(year, month, day)
    except:
        return jsonify({"message": "Bad request"}), HTTPStatus.BAD_REQUEST
    query = query.filter(func.DATE(Doctor.timestamp) == date_obj)
    return jsonify([doctor.to_dict() for doctor in query.all()])


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=8000)
