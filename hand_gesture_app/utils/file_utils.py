import cv2

# 加載提示圖片
def load_instruction_images():
    instruction_images = {}
    for hand in ['left', 'right']:
        for i in range(1, 6):
            image_path = f"./hand_gesture_app/resources/images/instruction_images/{hand}_{i}.png"
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"圖片未找到：{image_path}")
            key = f"{hand.capitalize()}_{i}"
            instruction_images[key] = img
    return instruction_images