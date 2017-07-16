#-*- coding utf-8 -*-
from flask import Flask, session
from flask import render_template
from flask import request
from lib.redis_session import *
import pymysql
from flask_s3 import FlaskS3
import boto
from boto.s3.key import Key
from flask import jsonify
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.session_interface = RedisSessionInterface(host="<REDISS_ENDPOINT>")

AWS_ACCESS_KEY_ID = '<AWS_ACCESS_KEY_ID>'
AWS_SECRET_ACCESS_KEY = '<AWS_SECRET_ACCESS_KEY>'
app.config['FLASKS3_BUCKET_NAME'] = '<FLASKS3_BUCKET_NAME>'
app.config['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
app.config['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
app.config['FLASKS3_REGION'] = '<FLASKS3_REGION>'
app.config['FLASKS3_CDN_DOMAIN'] = 'https://s3.'+app.config['FLASKS3_REGION']+'.amazonaws.com'
app.config['FLASKS3_BUCKET_DOMAIN'] = app.config['FLASKS3_CDN_DOMAIN']+'/'+app.config['FLASKS3_BUCKET_NAME']

app.config['FLASKS3_FORCE_MIMETYPE'] = True

s3 = FlaskS3(app)






@app.route('/',methods=['GET'])
def index():

    connection = pymysql.connect(host='<RDS_ENDPOINT>',
                             user='<USERNAME>',
                             password='<PASSWORD>',
                             db='<DBNAME>',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    sql = "SELECT * FROM `posts` \
            LEFT JOIN `users`ON `posts`.`user_id` = `users`.`id` \
            WHERE 1 ORDER BY `posts`.`id` DESC"
    cursor.execute(sql)
    posts = cursor.fetchall()

    connection.close()
    userName = request.args.get('name')

    return render_template('index.html',posts=posts,userName=userName)

@app.route('/post/<int:post_id>',methods=['GET'])
def post(post_id):
    connection = pymysql.connect(host='<RDS_ENDPOINT>',
                             user='<USERNAME>',
                             password='<PASSWORD>',
                             db='<DBNAME>',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    sql = "SELECT * FROM `posts` \
            LEFT JOIN `users`ON `posts`.`user_id` = `users`.`id` \
            WHERE `posts`.`id`="+str(post_id)+" ORDER BY `posts`.`id` DESC"
    cursor.execute(sql)
    post = cursor.fetchone()

    connection.close()
    return render_template('post.html',post=post)
@app.route('/signup',methods=['POST'])
def signup():
    userName = request.form['username']
    email = request.form['email']
    password = request.form['password']

    connection = pymysql.connect(host='<RDS_ENDPOINT>',
                             user='<USERNAME>',
                             password='<PASSWORD>',
                             db='<DBNAME>',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    try :
        if len(userName) == 0 or len(email) == 0 or len(password) == 0 :
            result = False
        else :
            sql = "INSERT INTO `users` (`id`, `user_name`, `user_email`, `user_password`) \
            VALUES (NULL, \'"+str(userName)+"\', \'"+str(email)+"\', \'"+str(password)+"\');"
            print sql
            cursor.execute(sql)
            connection.commit()
            print cursor.lastrowid
            result = True
    except Exception as e :
        print e
        result = False

    connection.close()

    return render_template('signup.html',result=result)



@app.route('/signin',methods=['POST'])
def signin():
    email = request.form['email']
    password = request.form['password']

    connection = pymysql.connect(host='<RDS_ENDPOINT>',
                             user='<USERNAME>',
                             password='<PASSWORD>',
                             db='<DBNAME>',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    try :
        if len(email) == 0 or len(password) == 0 :
            result = False
        else :
            sql = "SELECT * FROM `users` \
            WHERE `user_email` = \'"+str(email)+"\' \
            AND `user_password` = \'"+str(password)+"\'"
            print sql

            cursor.execute(sql)

            sql_result = cursor.fetchone()

            session['user_name'] = sql_result['user_name']
            session['user_id'] = sql_result['id']
            session.permanant = True

            result = True
    except Exception as e :
        print e
        result = False

    connection.close()

    return render_template('signin.html',result=result)

@app.route('/signout')
def signout():
    session.clear()
    return redirect('/')





@app.route('/posting',methods=['POST'])
def posting():
    title = request.form['title']
    picture_url = request.form['picture_url']
    content = request.form['content']
    user_id = session['user_id']
    connection = pymysql.connect(host='<RDS_ENDPOINT>',
                             user='<USERNAME>',
                             password='<PASSWORD>',
                             db='<DBNAME>',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()


    try :
        if len(title) == 0 or len(content) == 0 :
            result = False
        else :
            sql = "INSERT INTO `posts` (`id`, `title`, `content`,`user_id`,`picture_url`) \
            VALUES (NULL, \'"+str(title)+"\', \'"+str(content)+"\',\'"+str(user_id)+"\',\'"+str(picture_url)+"\');"
            print sql
            cursor.execute(sql)
            connection.commit()
            print cursor.lastrowid
            result = True
    except Exception as e :
        print e
        result = False

    connection.close()

    return jsonify(result=result)


@app.route('/file_upload', methods=['POST'])
def file_upload():
    s3 = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, host='s3-'+app.config['FLASKS3_REGION']+'.amazonaws.com')
    bucket_name = app.config['FLASKS3_BUCKET_NAME']
    bucket = s3.get_bucket(bucket_name)
    k = Key(bucket)
    data_file = request.files['0']
    file_contents = data_file.read()
    file_path = '/static/uploadedfiles/'+data_file.filename
    k.key = file_path
    k.set_contents_from_string(file_contents,policy='public-read')

    result ={}
    result['success'] = True
    result['url'] = app.config['FLASKS3_BUCKET_DOMAIN']+file_path

    return jsonify(result = result)





if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080,debug = True)
