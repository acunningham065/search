from flask import Flask, request, redirect, send_file, render_template
import mysql.connector
import os
import string

app = Flask(__name__, template_folder="templates/")

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


db_connection = mysql.connector.connect(
    host=os.environ.get("MYSQL_DB_HOST"),
    user=os.environ.get("MYSQL_DB_USER"),
    password=os.environ.get("MYSQL_DB_PASSWORD"),
    database=os.environ.get("MYSQL_DB_NAME"))


@app.route("/")
def index():
    if request.method == 'GET' and request.args.get('keywords') is not None:
        return search_results(request.args.get('keywords'))
    return render_template("templates/index.html")


def search_results(keywords):
    cursor = db_connection.cursor()
    try:
        individual_keywords = str(keywords).translate(str.maketrans('', '', string.punctuation)).split()
        print(individual_keywords)
        s_string = ""
        for count in range(len(individual_keywords)):
            s_string = s_string + "%s"
            if count != len(individual_keywords)-1:
                s_string = s_string + ","

        cursor.execute('SELECT DISTINCT url FROM pages WHERE word in (' + s_string + ')', individual_keywords)
        results = cursor.fetchmany(size=50)

        if not results:
            return render_template("templates/index.html", results="No Results Found")
        else:
            # display results
            results = list(map(lambda result: result[0], results))
            print(results)
            return render_template("index.html", results=results)
    except mysql.connector.Error as err:
        print("Error: {}".format(err))
        return "Error: {}".format(err)

if __name__ == '__main__':
    app.run()
