from datetime import datetime
from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_mysqldb import MySQL
import yaml
from datetime import datetime

app = Flask(__name__)
api=Api(app)

db = yaml.safe_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)


subscribe_post_args = reqparse.RequestParser()
subscribe_post_args.add_argument("email", type=str, help="email id is required", required=True)
subscribe_post_args.add_argument("topic", type=int, help="choose a topic", required=True)

content_post_args = reqparse.RequestParser()
content_post_args.add_argument("title", type=str, help="title is required", required=True)
content_post_args.add_argument("body", type=str, help="body is required", required=True)
content_post_args.add_argument("send_time", type=str, help="send_time is required", required=True)
content_post_args.add_argument("topic", type=int, help="choose a topic", required=True)

class Subscribe(Resource):
    def post(self):
        args = subscribe_post_args.parse_args()
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO subscribers(email, topic_id) VALUES(%s, %s)", (args['email'], args['topic']))
        mysql.connection.commit()
        cur.close()
        return 'success'

class Content(Resource):
    def post(self):
        args = content_post_args.parse_args()
        date = datetime.now()
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO content(title, body, create_time, send_time, topic_id) VALUES(%s, %s, %s, %s, %s)",
        (args['title'], args['body'], date, datetime.strptime(args['send_time'], "%Y/%m/%d, %H:%M:%S"), args['topic']))
        mysql.connection.commit()
        cur.close()
        return 'success'

api.add_resource(Subscribe, "/subscribe")
api.add_resource(Content, "/create")

if __name__=="__main__":
    app.run(debug=True)

