import numpy as np
from hand_gesture_app.utils.hand_landmark_utils import determine_hand_orientation, is_thumb_extended, is_finger_extended

# 計算手勢
def calculate_hand_gesture(landmarks, image_width, image_height):
    finger_tips_ids = [4, 8, 12, 16, 20]
    finger_states = []
    hand_orientation = determine_hand_orientation(landmarks, image_width, image_height)

    thumb_extended = is_thumb_extended(
        landmarks[finger_tips_ids[0]],
        landmarks[5],
        image_width,
        image_height,
        hand_orientation
    )
    finger_states.append(thumb_extended)

    for i, tip_id in enumerate(finger_tips_ids[1:], start=1):
        finger_tip_y = landmarks[tip_id].y * image_height
        mcp_joint_y = landmarks[tip_id - (3 if i == 1 else 2)].y * image_height
        finger_states.append(is_finger_extended(finger_tip_y, mcp_joint_y))

    if finger_states[1] and not any(finger_states[2:]):
        return "number 1"
    elif finger_states[1:3] == [True, True] and not any(finger_states[3:]):
        return "number 2"
    elif finger_states[1:4] == [True, True, True] and not finger_states[4]:
        return "number 3"
    elif all(finger_states[1:]) and not thumb_extended:
        return "number 4"
    elif all(finger_states):
        return "number 5"
    elif finger_states == [False, False, True, False, False]:
        return "Impolite!"
    else:
        return "Unrecognized gesture"
    
# 檢測OK手勢
def is_ok_gesture(landmarks, image_width, image_height):
    # 獲取拇指與食指指尖位置
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]

    # 轉換為像素座標
    thumb_tip_pos = np.array([thumb_tip.x * image_width, thumb_tip.y * image_height])
    index_tip_pos = np.array([index_tip.x * image_width, index_tip.y * image_height])

    # 計算距離
    distance = np.linalg.norm(thumb_tip_pos - index_tip_pos)

    # 獲取手的大小作為參考
    wrist = landmarks[0]
    middle_mcp = landmarks[9]
    wrist_pos = np.array([wrist.x * image_width, wrist.y * image_height])
    middle_mcp_pos = np.array([middle_mcp.x * image_width, middle_mcp.y * image_height])
    hand_size = np.linalg.norm(wrist_pos - middle_mcp_pos)

    # 判斷是否為OK手勢
    if distance < 0.2 * hand_size:
        return True
    else:
        return False