import cv2
import mediapipe as mp

# 初始化 MediaPipe 手部套件
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1
)
mp_drawing = mp.solutions.drawing_utils  # 繪圖工具

# 自定義手勢繪製函數（卡通效果）
def draw_custom_hand_landmarks(image, hand_landmarks):
    image_height, image_width = image.shape[:2]

    # 使用柔和、粉彩色繪製連線
    for connection in mp_hands.HAND_CONNECTIONS:
        start_idx = connection[0]
        end_idx = connection[1]
        start = hand_landmarks.landmark[start_idx]
        end = hand_landmarks.landmark[end_idx]
        start_point = (int(start.x * image_width), int(start.y * image_height))
        end_point = (int(end.x * image_width), int(end.y * image_height))
        
        # 粉藍色連線，線條較細
        cv2.line(image, start_point, end_point, (180, 220, 240), 3)

    # 使用粉彩粉紅色繪製節點，帶來柔和、平和的效果
    for idx, landmark in enumerate(hand_landmarks.landmark):
        x = int(landmark.x * image_width)
        y = int(landmark.y * image_height)
        
        # 小型粉紅色圓點，溫和的視覺效果
        cv2.circle(image, (x, y), 5, (255, 204, 204), -1)  # 粉紅色節點