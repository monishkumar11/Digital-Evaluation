
from datetime import datetime
import os
import pprint

from flask import Flask, request, render_template
import easyocr
import difflib
import spacy



app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__)) # project abs path


@app.route("/")
def index():
    return render_template("upload.html")


@app.route("/upload_page", methods=["GET"])
def upload_page():
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload():
    # folder_name = request.form['uploads']
    target = os.path.join(APP_ROOT, 'static/')
    print(target)
    if not os.path.isdir(target):
        os.mkdir(target)
    print(request.files.getlist("file"))
    option = request.form.get('optionsPrediction')
    print("Selected Option:: {}".format(option))
    for upload in request.files.getlist("file"):
        print(upload)
        print("{} is the file name".format(upload.filename))
        filename = upload.filename
        # This is to verify files are supported
        ext = os.path.splitext(filename)[1]
        if (ext == ".jpg") or (ext == ".png"):
            print("File supported moving on...")
        else:
            render_template("Error.html", message="Files uploaded are not supported...")
        savefname = datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + "."+ext
        destination = "/".join([target, savefname])
        print("Accept incoming file:", filename)
        print("Save it to:", destination)
        upload.save(destination)
        teststr, matchstr, predict, grade = easyocrverification(destination,savefname)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(predict)
        pp.pprint(grade)
        return render_template("complete.html", image_name=savefname, result=teststr,predict=predict,grade=grade)


def easyocrverification(destination,savefname):
    reader = easyocr.Reader(['en'])
    data = reader.readtext(destination)
    pp = pprint.PrettyPrinter(indent=4)
    environ = 'environment '

    test = difflib.SequenceMatcher(None)
    test.set_seq2(environ)
    count = 0
    teststr=""
    percent=0
    matchstr =""


    for text in data:
        teststr = teststr +" "+ text[-2]

    nlp = spacy.load('en_core_web_md')
    pp.pprint(teststr)
    tokens = nlp(teststr)
    keys = nlp(environ)
    matchstr=""
    ration1=0
    for key in keys:
        for token in tokens:
            pp.pprint(token.text)
            ration1 = difflib.SequenceMatcher(None,  token.text, key.text).ratio()
            pp.pprint(ration1)
            if ration1 > 0.75 and not matchstr.__contains__(token.text):
                percent = percent + ration1
                matchstr = matchstr+ " "+token.text

    pp.pprint(matchstr.lstrip().casefold())
    predict = difflib.SequenceMatcher(None, matchstr.lstrip().casefold(), environ.casefold()).ratio()
    pp.pprint(predict)

    if predict <= 0.45:
        grade = "C"
    elif predict > 0.45 and predict <= 0.60:
        grade = "B"
    elif predict > 0.60 and predict <= 0.80:
        grade = "B+"
    elif predict > 0.80 and predict <= 0.90:
        grade = "A"
    elif predict > 0.90 and predict <= 0.95:
        grade = "A+"
    else:
        grade = "O"

    return teststr, matchstr, predict, grade


if __name__ == "__main__":
    app.run(port=4555, debug=True)