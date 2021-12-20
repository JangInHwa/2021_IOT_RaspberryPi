import cv2

cam = cv2.VideoCapture('output.avi')

if not cam.isOpened():
	print('Camera open failed')
	exit()

# ret, frame = cam.read()
# cv2.imshow('frame', frame)
# cv2.imwrite('output.jpg', frame)
# cv2.waitKey(0)


while True:
	ret, frame = cam.read()
	if not ret:
		break
	cv2.imshow('original', frame)
	cv2.imshow('gray', cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
	cv2.imshow('edge', cv2.Canny(frame, 50, 100))
	if cv2.waitKey(10) == 13:
		break

cam.release()
cv2.destroyAllWindows()
