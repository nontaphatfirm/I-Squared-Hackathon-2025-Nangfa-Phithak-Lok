import gradio as gr
import cv2
import requests
import os
 
from ultralytics import YOLO


file_urls = ['https://www.dropbox.com/scl/fi/xkwmzp7z0yopab16d6ueu/2025.jpg?rlkey=lmthnvuhs567kf1kdix6wo4nc&st=23h1mdjy&dl=1','https://www.dropbox.com/scl/fi/sxg1bsrpj8re622h5jk4c/2029.jpg?rlkey=z5fwvc2dbjhguicu79v3l74dp&st=xopz7i1i&dl=1','https://www.dropbox.com/scl/fi/e36ni8t2372ug8bgd9flg/8566.jpg?rlkey=j2dudcwakpa69nwsm4p9isogr&st=bhz51tu9&dl=1']

def download_file(url, save_name):
    url = url
    if not os.path.exists(save_name):
        file = requests.get(url)
        open(save_name, 'wb').write(file.content)
 
for i, url in enumerate(file_urls):
    download_file(
        file_urls[i],
        f"image_{i}.jpg"
    )

model = YOLO('best.pt')
path  = ['image_0.jpg','image_1.jpg','image_2.jpg']

outputs = model.predict(path)
results = outputs[0].cpu().numpy()

def show_preds_image(image_path):
    image = cv2.imread(image_path)
    outputs = model.predict(source=image_path)
    results = outputs[0].cpu().numpy()

    # Define colors for classes (BGR format)
    class_colors = {
        0: (0, 255, 0),      # green for class 0
        1: (255, 0, 0),      # blue for class 1
        2: (0, 0, 255),      # red for class 2
        3: (0, 255, 255),    # yellow for class 3
        4: (255, 0, 255),    # magenta for class 4
        5: (225, 225, 0)
        # Add more if your model has more classes
    }

    for i, det in enumerate(results.boxes.xyxy):
        cls_id = int(results.boxes.cls[i])  # get class index
        color = class_colors.get(cls_id, (255, 255, 255))  # default to white if not defined

        cv2.rectangle(
            image,
            (int(det[0]), int(det[1])),
            (int(det[2]), int(det[3])),
            color=color,
            thickness=2,
            lineType=cv2.LINE_AA
        )

        # Optional: draw class label text on top
        class_name = model.names[cls_id]  # Get class name from model
        cv2.putText(image, class_name, (int(det[0]), int(det[1]) - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

 
inputs_image = [
    gr.components.Image(type="filepath", label="Input Image"),
]
outputs_image = [
    gr.components.Image(type="numpy", label="Output Image"),
]
interface_image = gr.Interface(
    fn=show_preds_image,
    inputs=inputs_image,
    outputs=outputs_image,
    title="liver thing idk",
    examples=path,
    cache_examples=False,
)


gr.TabbedInterface(
    [interface_image],
    tab_names=['Image inference']
).queue().launch()