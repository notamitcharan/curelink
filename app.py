from datetime import datetime
from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_mysqldb import MySQL
import yaml
from datetime import datetime
from flask_mail import Mail, Message



app = Flask(__name__)
api=Api(app)



db = yaml.safe_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']


mysql = MySQL(app)


mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT" : 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'amithatecovid@gmail.com',
    "MAIL_PASSWORD": db['mail_pwd'],
}


app.config.update(mail_settings)
mail = Mail(app)



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

        cur.execute(f"SELECT email FROM subscribers WHERE topic_id={args['topic']}")
        substuple = cur.fetchall()
        subs = list(substuple[0])

        cur.execute(f"SELECT name FROM topics WHERE id={args['topic']}")
        top = cur.fetchone()

        cur.close()

        msg = Message(f"{args['title']}", sender='no-reply@test.com', recipients=subs)
        msg.body = f"Here is your newsletter on {top[0]}.\nToday's topic is {args['title']}.\n\n{args['body']}"
        mail.send(msg)
        return 'success'


api.add_resource(Subscribe, "/subscribe")
api.add_resource(Content, "/create")


if __name__=="__main__":
    app.run(debug=True, host='0.0.0.0')