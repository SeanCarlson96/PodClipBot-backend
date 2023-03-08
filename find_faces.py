import cv2

# face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def find_face_center(frame, face_cascade):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        return (x + w/2, y + h/2)
    else:
        return None
