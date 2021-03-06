import numpy as np
import cv2

model_path = "yolov5/seeds/train_50/weights/best.onnx"
image_path = "datasets/my_seed/4x_Resize/Im_20220422_175412_1348_B.png"
label_path = "datasets/my_seed/4x_Resize/Im_20220422_175412_1348_B.txt"
inp_sz = 512

# step 1 - load the model

net = cv2.dnn.readNet(model_path)

# step 2 - feed a 512*512 image to get predictions

def format_yolov5(frame):

    row, col, _ = frame.shape
    _max = max(col, row)
    result = np.zeros((_max, _max, 3), np.uint8)
    result[0:row, 0:col] = frame
    return result

image = cv2.imread(image_path)
input_image = format_yolov5(image) # making the image square
blob = cv2.dnn.blobFromImage(input_image , 1/255.0, (inp_sz, inp_sz), swapRB=True)
net.setInput(blob)
predictions = net.forward()

# step 3 - unwrap the predictions to get the object detections 

class_ids = []
confidences = []
boxes = []

output_data = predictions[0]

image_width, image_height, _ = input_image.shape
x_factor = image_width / inp_sz
y_factor =  image_height / inp_sz

rnge = len(output_data)
for r in range(rnge): #16128
    row = output_data[r]
    confidence = row[4]
    if confidence >= 0.4:

        classes_scores = row[5:]
        _, _, _, max_indx = cv2.minMaxLoc(classes_scores)
        class_id = max_indx[1]
        if (classes_scores[class_id] > .25):

            confidences.append(confidence)

            class_ids.append(class_id)

            x, y, w, h = row[0].item(), row[1].item(), row[2].item(), row[3].item() 
            left = int((x - 0.5 * w) * x_factor)
            top = int((y - 0.5 * h) * y_factor)
            width = int(w * x_factor)
            height = int(h * y_factor)
            box = np.array([left, top, width, height])
            boxes.append(box)

class_list = []
with open(label_path, "r") as f:
    class_list = [cname.strip() for cname in f.readlines()]
    
class_list = class_list[0].split(' ')

indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.25, 0.45) 

result_class_ids = []
result_confidences = []
result_boxes = []

for i in indexes:
    result_confidences.append(confidences[i])
    result_class_ids.append(class_ids[i])
    result_boxes.append(boxes[i])

for i in range(len(result_class_ids)):

    box = result_boxes[i]
    class_id = result_class_ids[i]

    cv2.rectangle(image, box, (0, 255, 255), 2)
    cv2.rectangle(image, (box[0], box[1] - 20), (box[0] + box[2], box[1]), (0, 255, 255), -1)
    cv2.putText(image, class_list[class_id], (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, .5, (0,0,0))

cv2.imwrite("misc/kids_detection.png", image)
cv2.imshow("output", image)
cv2.waitKey()