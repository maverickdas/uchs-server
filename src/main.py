import os
import yaml

from flask import Flask, request, jsonify
import pymysql

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

app = Flask(__name__)


@app.route('/uchs-db')
def main():
    # When deployed to App Engine, the `GAE_ENV` environment variable will be
    # set to `standard`
    if os.environ.get('GAE_ENV') == 'standard':
        # If deployed, use the local socket interface for accessing Cloud SQL
        unix_socket = '/cloudsql/{}'.format(db_connection_name)
        cnx = pymysql.connect(user=db_user, password=db_password,
                              unix_socket=unix_socket, db=db_name)
    else:
        # If running locally, use the TCP connections instead
        # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
        # so that your application can use 127.0.0.1:3306 to connect to your
        # Cloud SQL instance
        host = '127.0.0.1'
        cnx = pymysql.connect(user=db_user, password=db_password,
                              host=host, db=db_name)

    with cnx.cursor() as cursor:
        cursor.execute('SELECT NOW() as now;')
        result = cursor.fetchall()
        current_time = result[0][0]
    cnx.close()

    return str(current_time)


@app.route('/')
def test1():
    response = {"data": "Welcome to UCHS-Server!", "status": "OK"}
    return jsonify(response)


@app.route('/testname', methods=['GET'])
def test():
    name = request.args.get('name')
    reponse = {"data": name, "status": "OK"}
    return jsonify(reponse)


if __name__ == '__main__':
    if not os.environ.get('GAE_ENV') == 'standard':
        with open("app.yaml") as f:
            env = yaml.load(f, Loader=yaml.BaseLoader)["env_variables"]
        for k, v in env.items():
            os.environ[k] = v
    app.run(host='127.0.0.1', port=8080, debug=True)
