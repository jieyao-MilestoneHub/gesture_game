import numpy as np

# 判斷手的朝向
def determine_hand_orientation(landmarks, image_width, image_height):
    wrist_pos = np.array([landmarks[0].x * image_width, landmarks[0].y * image_height])
    middle_finger_tip_pos = np.array([landmarks[12].x * image_width, landmarks[12].y * image_height])
    vector_wrist_to_middle_tip = middle_finger_tip_pos - wrist_pos
    if vector_wrist_to_middle_tip[1] > 0:
        return "Palm Up"
    else:
        return "Palm Down"
    
# 判斷大拇指是否伸直
def is_thumb_extended(thumb_tip, index_mcp, width, height, hand_orientation):
    thumb_tip_pos = np.array([thumb_tip.x * width, thumb_tip.y * height])
    index_mcp_pos = np.array([index_mcp.x * width, index_mcp.y * height])
    vector_thumb_to_index = thumb_tip_pos - index_mcp_pos
    distance = np.linalg.norm(vector_thumb_to_index)

    distance_threshold = width * 0.1 if hand_orientation == "Palm Down" else width * 0.075
    return distance > distance_threshold

# 判斷指尖是否伸直
def is_finger_extended(finger_tip_y, mcp_joint_y):
    return finger_tip_y < mcp_joint_y