import os

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import dotenv
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from marshmallow import Schema, fields

dotenv.load_dotenv()

db_user = os.environ.get('DB_USERNAME')
db_pass = os.environ.get('DB_PASSWORD')
db_hostname = os.environ.get('DB_HOSTNAME')
db_name = os.environ.get('DB_NAME')

DB_URI = 'mysql+pymysql://{db_username}:{db_password}@{db_host}/{database}'.format(db_username=db_user, db_password=db_pass, db_host=db_hostname, database=db_name)

engine = create_engine(DB_URI, echo=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, primery_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    collphone = db.Column(db.String(13), unique=True, nullable=False)

    @classmethod
    def get_all(cls):
        return cls.query.all()
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class StudentScrema(Schema):
    id = fields.Integer()
    name = fields.Str()
    email = fields.Str()
    age = fields.Integer()
    cellphone = fields.Str()

student_screma = StudentScrema    

@app.route('/', methods = ['GET'])
def home():
    return '<p>Hello from students API!</p>', 200

@app.route('/api', methods = ['GET'])
def api_main():
    return jsonify('Hello, World!'), 200

@app.route('/api/students', methods = ['GET'])
def get_all_students():
    students = Student.get.all()
    student_list = StudentScrema(many=True)
    response = student_list.dump(students)
    return jsonify(response), 200

@app.route('/api/students/get/<int:id>', methods = ['GET'])
def get_student(id):
    student_info = Student.get_by_id(id)
    serializer = StudentScrema()
    response = serializer.dump(student_info)
    return jsonify(response), 200

@app.route('/api/students/add', methods = ['POST'])
def add_student(id):
    json_data = request.get_json()
    new_student = Student(
        name= json_data.get('name'),
        email= json_data.get('email'),
        age= json_data.get('age'),
        cellphone= json_data.get('cellphone')
    )
    new_student.save()
    serializer = StudentScrema()
    data = serializer.dump(new_student)
    return jsonify(data), 201

if __name__== '__main__':
    if not database_exists(engine.url):
        create_database(engine.url)
    db.create_all()
    app.run(debug=True)