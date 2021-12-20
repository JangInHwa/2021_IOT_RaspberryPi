import cv2

cam = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier('./xml/face.xml')

if not cam.isOpened():
    print('Camera open failed')
    exit()

while True:
    ret, frame = cam.read()
    if not ret:
        break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x,y), (x+w, y+h), (255, 0, 0), 2)    

    cv2.imshow('frame', frame)

    if cv2.waitKey(10) == 13:
        break

cv2.waitKey(0)

cam.release()
cv2.destroyAllWindows()
