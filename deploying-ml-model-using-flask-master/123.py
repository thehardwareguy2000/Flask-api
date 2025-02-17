from flask import Flask, render_template,url_for,request
import pickle
from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import imutils
import cv2
app = Flask(__name__)
model=ludwigModel.load('model')

######################################################
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/registerV')
def registerV():
    return render_template('registerV.html')



###############################################################


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict', methods = ['POST'])
def predict():
    image = cv2.imread("test.jpg")
    print(image.shape)


    workbook = xlsxwriter.Workbook('Attendence.xlsx')
    worksheet = workbook.add_worksheet("sheet")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)
#cv2.imshow("Original", image)

    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    docCnt = None

    if len(cnts) > 0:

            cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
            for c in cnts:
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                if len(approx) == 4:
                    docCnt = approx
                    break
            else :
                print("get the picture of full image")
    
    

    paper = four_point_transform(image, docCnt.reshape(4, 2))
    warped = four_point_transform(gray, docCnt.reshape(4, 2))
#otsu threshold algo
    thresh = cv2.threshold(warped, 0, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    questionCnts = []


    for c in cnts:
	
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)

	
        if w >= 10 and h >= 20 and ar >= 0.9 and ar <= 1.1:
            questionCnts.append(c)


    questionCnts = contours.sort_contours(questionCnts,method="top-to-bottom")[0]
    correct = 0
    roll=8312
#col = 0
    row = 0
    for (q, i) in enumerate(np.arange(0, len(questionCnts), 5)):

        cnts = contours.sort_contours(questionCnts[i:i + 5])[0]
        bubbled = None
        g =0
        col = 0
        z=1
        for (j, c) in enumerate(cnts):
            mask = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)
    
            mask = cv2.bitwise_and(thresh, thresh, mask=mask)
            total = cv2.countNonZero(mask)
            
            bubbled = (total, j)
            if bubbled > (1000,0):
                g = g + 1
                print(z)
                
            z=z+1
        score = (g / 5.0) * 100
        print(roll,":-",score)
        print("-----------------------------------------")
        worksheet.write(row, col, roll) 
        worksheet.write(row, col + 1, score) 
        row += 1
        roll=roll+1
	
        
    workbook.close()
    if request.method == 'POST':
        comment = request.form['comment']
        data = [comment]
    return render_template('result.html', prediction = my_prediction)


if __name__ == '__main__':
	app.run(debug=True)
