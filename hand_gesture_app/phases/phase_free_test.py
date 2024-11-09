import time
from hand_gesture_app.phases.phase_common import show_stage_intro
from hand_gesture_app.utils.image_utils import draw_text_centered, draw_text

# 測試階段1:自由測試階段
def free_testing_phase(vars, hand_label, number, combined_image):
    if vars['stage_intro']:
        show_stage_intro(vars, combined_image)
        return

    # 檢查是否超過設定的時間
    if time.time() - vars['stage_start_time'] >= vars['question_duration']:
        # 計算階段花費的時間
        vars['phase_time_spent'] = time.time() - vars['stage_start_time']
        vars['stage_start_time'] = time.time()

        # 結束階段，進入下一階段
        vars['stage'] += 1
        vars['stage_intro'] = True
        return

    # 顯示提示文字
    draw_text_centered(combined_image, "Feel free to test gestures", 1, (255, 255, 255), 2)

    # 顯示當前檢測到的手勢
    if hand_label and number:
        text = f"Hand: {hand_label}, Number: {number}"
        draw_text(combined_image, text, (10, 40), 1, (255, 255, 255), 2)

    # 顯示時間
    current_time = int(time.time() - vars['stage_start_time'])
    draw_text(
        combined_image,
        f"Time: {current_time}s",
        (10, combined_image.shape[0] - 20),
        1,
        (255, 255, 255),
        2
    )