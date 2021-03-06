from flask import Flask, request, render_template
import mysql.connector
import string
import requests
import json
import sys

app = Flask(__name__, template_folder="templates/")

ADVERT_SERVICE_URL = None
db_connection = None


@app.route("/")
def index():
    if request.method == 'GET' and request.args.get('keywords') is not None:
        return search_results(request.args.get('keywords'))
    return render_template("index.html")


def search_results(keywords):
    cursor = db_connection.cursor()
    try:
        individual_keywords = str(keywords).translate(str.maketrans('', '', string.punctuation)).split()
        s_string = ""
        for count in range(len(individual_keywords)):
            s_string = s_string + "%s"
            if count != len(individual_keywords)-1:
                s_string = s_string + ","

        cursor.execute('SELECT DISTINCT url FROM pages WHERE word in (' + s_string + ')', individual_keywords)
        results = cursor.fetchmany(size=50)

        if not results:
            return render_template("index.html", results=["No Results Found"])
        else:
            # display results
            results = list(map(lambda result: result[0], results))
            try:
                adverts = json.loads(requests.post(url=ADVERT_SERVICE_URL + "/?" + keywords).content)
                return render_template("index.html", results=results, adverts=adverts if adverts is not None else ["No adverts found"])
            except requests.exceptions.InvalidSchema or requests.exceptions.ConnectionError:
                return render_template("index.html", results=results, adverts=["Advert service could not be reached"])
    except mysql.connector.Error as err:
        print("Error: {}".format(err))
        return "Error: {}".format(err)


if __name__ == '__main__':
    try:
        db_connection = mysql.connector.connect(
            host=sys.argv[1],
            user=sys.argv[2],
            password=sys.argv[3],
            database=sys.argv[4])
    except mysql.connector.Error as err:
        print("Error: {}".format(err))

    if len(sys.argv) == 6:
        ADVERT_SERVICE_URL = sys.argv[5]
    app.run(host="0.0.0.0", port=5025)
