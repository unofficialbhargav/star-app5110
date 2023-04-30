import os
import psycopg2
import jinja2
from flask import Flask, redirect, request, render_template, url_for, session, flash
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = 'I Understand Databases'

def get_db_connection():

    result = urlparse(os.environ['DATABASE_URL'])
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    connection = psycopg2.connect(
        database=database,
        user=username,
        password=password,
        host=hostname,
        port=port
    )

    return connection

@app.route("/", methods=["GET", "POST"])
def index():
	return render_template('index.html')

@app.route("/query", methods=["GET", "POST"])
def query():
	cur = get_db_connection().cursor()
	
	query='''
	SELECT *
	FROM
	(
	SELECT p_a.project, p_a.general_developer, p_a.developer, p_a.grade,
	ROUND(s_m.take_up, 0) AS take_up, ROUND(s_m.take_up_value, 0) AS take_up_value, 
	s_m.lot_tcp_low, s_m.lot_tcp_high, s_m.lot_tcp_average,
	s_m.house_lot_tcp_low, s_m.house_lot_tcp_high, s_m.house_lot_tcp_average,
	m_a.metro_area, d.quarter, d.year
	FROM date d, sales_metrics s_m, project_attributes p_a, project_plotting p_p, metro_area m_a
	WHERE d.date = s_m.period
	AND s_m.serial_code = p_a.serial_code
	AND p_a.project_code = p_p.project_code
	AND p_p.ph_psgc = m_a.ph_psgc
	AND p_a.general_developer = '{}'  			--change general developer when needed
	AND p_a.grade = '{}'							--change grade when needed
	AND d.quarter = '{}' 							--change quarter when needed
	AND d.year = '{}'								--change year when needed
	ORDER BY take_up DESC	
	) AS result
	WHERE result.take_up IS NOT NULL;
	'''.format(request.form['gd'], 
		request.form['grade'], 
		request.form['quarter'], 
		request.form['year'])
	#return render_template('query.html')
	cur.execute(query)
	properties=cur.fetchall()
	return render_template('query.html', properties=properties)

@app.errorhandler(404)
def error404(e):
    return render_template('404.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)	