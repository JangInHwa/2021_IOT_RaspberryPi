from flask import Flask, render_template
import os
import dir_search

# Flask 객체 생성
# __name__은 파일명
app = Flask(__name__)


#메인 뷰
@app.route("/")
def home():
    imageNameSet = []
    try: 
        path = ''.join([os.getcwd(),"/static/images"])
        imageNameSet = dir_search.search(path) #static/images/ 디렉토리 밑에있는 파일을 전부 불러옴
        print(imageNameSet)
    except Exception as e: 
        print(e)
    return render_template("index.html", imageNames = imageNameSet)


# 터미널에서 직접 실행시킨 경우
if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0")
    finally:
        print("clean up")
