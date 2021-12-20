import cv2

img = cv2.imread('bts.jpg')
img2 = cv2.resize(img, (600,200))

gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

cv2.imshow('BTS', img2)
cv2.imshow('BTS_GRAY', gray)

while True:
	if cv2.waitKey() == ord('d'):
		break

cv2.imwrite('btsgray.jpg', gray)

cv2.destroyAllWindows()
