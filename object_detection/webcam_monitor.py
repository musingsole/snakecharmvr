import cv2

device = 0
name = "webcam1"
buffer = 100

cv2.namedWindow("preview")
vc1 = cv2.VideoCapture(device)

if vc1.isOpened():  # try to get the first frame
    rval, frame = vc1.read()
else:
    rval = False

index = 0
while rval:
    index = index + 1 if index < buffer else 0
    cv2.imshow("preview", frame)
    cv2.imwrite(f"input/{name}_{index}.jpg", frame)
    rval, frame = vc1.read()
    key = cv2.waitKey(20)
    if key == 27:  # exit on ESC
        break
cv2.destroyWindow("preview")
