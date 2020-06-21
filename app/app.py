from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import json
from bson.objectid import ObjectId
import pymongo
import math    
import mongoengine as me
from flask_mongoengine import MongoEngine
from bson import json_util
import pandas as pd
import RecommendationEngine
from sklearn.preprocessing import MinMaxScaler


app = Flask(__name__)
#mongo = PyMongo(app,uri="mongodb://localhost:27017/wevioo")
#mongodb+srv://root:<password>@cluster0-rmqjn.mongodb.net/test
#mongo = PyMongo(app,uri="mongodb://localhost:27017/wevioo")

#app.config['MONGODB_SETTINGS'] = {
#    'db': 'wevioo',
#    'host': 'localhost',
#    'port': 27017
#}

app = Flask(__name__)

mongo = PyMongo(app,uri="mongodb://root:root@mongodb:27017/wevioo?authSource=admin")

app.config['MONGODB_SETTINGS'] = {
    'db': 'wevioo',
    'host': 'mongodb://root:root@mongodb:27017/wevioo?authSource=admin'
}

db = MongoEngine()
db.init_app(app)


#*******************************Profile*********************************

class Skill(me.EmbeddedDocument):
    name = me.StringField()
    coeff = me.IntField()

class Profile(me.Document):
    name = me.StringField()
    skills = me.ListField(me.EmbeddedDocumentField(Skill))
    def to_json(self):
        return {"name": self.name,
                "skills": self.skills}


@app.route('/profile', methods=['GET'])
def get_all_profiles():
    
    profiles = Profile.objects
    return jsonify(profiles)

@app.route('/profile', methods=['POST'])
def add_profile():
    request_body = request.get_json()
    profile_name = request_body['name']
    skills = request_body['skills']
        
    profile = Profile(name=profile_name)

    for skill in skills:
        profile.skills.append(Skill(name=skill['name'],coeff=int(skill['coeff'])))

    profile.save()
    return jsonify(profile)

@app.route('/profile', methods=['GET'])
def list_profile():
    profile_collection = mongo.db.profile

    profiles = profile_collection.find()

    return jsonify(profiles)

#*******************************/Profile*********************************



#*******************************Recommendation*********************************


@app.route("/recommended/<id>")
def get_recommended_profiles(id):
    #Connecting to labeled db collection
    labeled_db_collection = mongo.db.labeled_db

    df = pd.DataFrame(list(labeled_db_collection.find({}, {'_id': False})))

    scaler = MinMaxScaler()

    column_list = ['total_experience', 'stability', 'location', 'backend', 'frontend', 'phpsymfony', 'ArchitecteJee',
               'Embedded', 'fullstackjs', 'java/jee', 'DRUPAL', 'PO']

    df[column_list] = scaler.fit_transform(df[column_list])
    profile_list = json.loads(df.to_json(orient='records'))
    print(df.head())
    profile_vector_list = []
    #just to ignore error
    profile_to_test = {'id':""}
    for profile in profile_list:
        if profile['id'] == id:
            profile_to_test = RecommendationEngine.RecommendationEngine.profile_to_vector(profile)
            #print(profile_to_test)
        else:
            profile_vector_list.append(RecommendationEngine.RecommendationEngine.profile_to_vector(profile))
    lise_recommended = RecommendationEngine.RecommendationEngine.get_similar_profiles(profile_to_test, profile_vector_list,10)
    return jsonify(lise_recommended)

#*******************************/Recommendation****************************************


@app.route("/upload_databases")
def upload_databases():
    database_brute_collection = mongo.db['database_brute']

    with open('database_brute.json', 'r',encoding='utf-8') as f:
        file_data = [json.loads(line) for line in f]  # load data from JSON to dict
    database_brute_collection.insert_many(file_data)
    return 'database_brute uploaded'


#************************************************************************************

@app.route("/users/<id>")
def get_user_by_id(id):
	#Connecting to labeled db collection
    database_brute_collection = mongo.db.database_brute

    #Find user by its id 
    user = database_brute_collection.find_one_or_404({'_id': ObjectId(id)})

    user_info = {'id':str(user['_id']),'url': user['url'],'personal_info':user['personal_info'],'skills':user['skills'],
    'experiences':user['experiences']}
    return jsonify(user_info)


@app.route("/users")
def get_all_users_with_pagination():

	request_body = request.get_json()

	#Connecting to labeled db collection
	labeled_db_collection = mongo.db.labeled_db

	offset = int(request.args['offset'])
	limit = int(request.args['limit'])

	users = labeled_db_collection.find().skip(offset).limit(limit)

	number_of_pages = math.ceil(users.count()/limit)
	number_of_users = users.count()


	output = []
	for user in users:
		output.append({'id': user['id'],
			'labels':{'backend':user['backend'],'frontend':user['frontend'],'phpsymfony':user['phpsymfony'],'ArchitecteJee':user['ArchitecteJee'],'Embedded':user['Embedded'],'fullstackjs':user['fullstackjs'],'java/jee':user['java/jee'],'DRUPAL':user['DRUPAL'],'PO':user['PO']},
			'scores':{'score_backend':user['score_backend'],'score_frontend':user['score_frontend'],'phpsymfony':user['phpsymfony'],'score_ArchitecteJee':user['score_ArchitecteJee'],'score_Embedded':user['score_Embedded'],'score_fullstackjs':user['score_fullstackjs'],'score_java/jee':user['score_java/jee'],'score_DRUPAL':user['score_DRUPAL'],'score_PO':user['score_PO']}})
	return jsonify({'count':number_of_users,'pages':number_of_pages,'labeled_users': output})

@app.route('/users', methods=['POST'])
def get_all_users_with_pagination_and_filters():
    request_body = request.get_json()
    #Connecting to labeled db collection
    labeled_db_collection = mongo.db.labeled_db
    
    offset = int(request.args['offset'])
    limit = int(request.args['limit'])

    min_experience = int(request_body['min_experience'])*12
    max_experience = int(request_body['max_experience'])*12
    min_stability= float(request_body['min_stability'])*12
    max_stability= float(request_body['max_stability'])*12
    #cast school string array to school int array
    school = request_body['school']
    int_school_array = [int(numeric_string) for numeric_string in school]
    print(school)
    location = int(request_body['location'])
    profile = request_body['profile']
    score= 'score_'+profile
    users = labeled_db_collection.find({profile :{ '$eq' : 1},'total_experience':{'$gte': min_experience,'$lte':max_experience},
    'stability':{'$gte': min_stability,'$lte':max_stability},
    'school':{'$in' : int_school_array },'location':location}).sort(score,pymongo.DESCENDING).skip(offset).limit(limit)

    number_of_pages = math.ceil(users.count()/limit)
    number_of_users = users.count()
    output = []
    for user in users:
        output.append({'id': user['id'],
            'labels':{'backend':user['backend'],'frontend':user['frontend'],'phpsymfony':user['phpsymfony'],'ArchitecteJee':user['ArchitecteJee'],'Embedded':user['Embedded'],'fullstackjs':user['fullstackjs'],'java/jee':user['java/jee'],'DRUPAL':user['DRUPAL'],'PO':user['PO']},
            'scores':{'score_backend':user['score_backend'],'score_frontend':user['score_frontend'],'phpsymfony':user['phpsymfony'],'score_ArchitecteJee':user['score_ArchitecteJee'],'score_Embedded':user['score_Embedded'],'score_fullstackjs':user['score_fullstackjs'],'score_java/jee':user['score_java/jee'],'score_DRUPAL':user['score_DRUPAL'],'score_PO':user['score_PO']}})
    return jsonify({'count':number_of_users,'pages':number_of_pages,'labeled_users': output})



#allow cors access
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


app.run(debug=True,port=2999)

