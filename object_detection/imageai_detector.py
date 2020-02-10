from imageai.Detection import ObjectDetection
from datetime import datetime

detector = ObjectDetection()

model_path = "./models/yolo-tiny.h5"
input_path = "./input/webcam1_{index}.jpg"
output_path = "./output/webcam1_{index}_yolo_detected.jpg"

detector.setModelTypeAsTinyYOLOv3()
detector.setModelPath(model_path)
detector.loadModel()


def detect(index):
    detection = detector.detectObjectsFromImage(
        input_image=input_path.format(index=index),
        output_image_path=output_path.format(index=index)
    )

    for eachItem in detection:
        print(eachItem["name"], " : ", eachItem["percentage_probability"])


if __name__ == "__main__":
    for i in range(100):
        s = datetime.utcnow()
        print(f"{s} | Starting {i}")
        detect(index=i)
        runtime = datetime.utcnow() - s
        print(f"{datetime.utcnow()} | Completed {i} | Runtime: {runtime}")
