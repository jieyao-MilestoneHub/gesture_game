import time
import random
import cv2
from hand_gesture_app.utils.image_utils import draw_text, draw_text_centered
from hand_gesture_app.phases.phase_common import show_stage_intro, game_over

# 測試階段2: 數字測試階段
def number_testing_phase(vars, hand_label, number, combined_image):
    if vars['stage_intro']:
        show_stage_intro(vars, combined_image)
        return

    # 顯示時間（持續顯示）
    current_time = int(time.time() - vars['stage_start_time'])
    draw_text(
        combined_image,
        f"Time: {current_time}s",
        (10, combined_image.shape[0] - 20),
        1,
        (255, 255, 255),
        2
    )

    # 檢查是否超過設定的時間
    if time.time() - vars['stage_start_time'] >= vars['question_duration']:
        # 計算階段花費的時間
        vars['phase_time_spent'] = time.time() - vars['stage_start_time']
        vars['stage_start_time'] = time.time()

        # 結束階段，進入下一階段
        vars['stage'] += 1
        vars['stage_intro'] = True
        return

    if vars['question'] == "":
        vars['target_number'] = random.randint(1, 5)
        vars['question'] = f"Show number: {vars['target_number']}"
        vars['question_start_time'] = time.time()
        vars['answered_current_question'] = False

    # 繪製題目
    draw_text(combined_image, vars['question'], (10, 40), 1, (255, 255, 255), 2)

    current_time = time.time()

    # 如果正在顯示回饋訊息，停止手勢偵測
    if vars.get('feedback_active', False):
        elapsed_feedback_time = current_time - vars['feedback_start_time']
        if elapsed_feedback_time <= 1.5:  # 持續顯示回饋1.5秒
            color = (0, 255, 0) if vars['answer_feedback'] == "Correct!" else (0, 0, 255)
            draw_text_centered(combined_image, vars['answer_feedback'], 2, color, 3)
        else:
            vars['answer_feedback'] = ""  # 清除回饋訊息
            vars['feedback_active'] = False  # 恢復手勢偵測
        return

    # 檢查是否已回答
    if vars['answered_current_question']:
        vars['question'] = ""
        vars['gesture_start_time'] = None
        vars['current_gesture'] = None
        vars['answer_feedback'] = ""  # 清除回饋訊息
        return

    if number is None:
        vars['gesture_start_time'] = None
        vars['current_gesture'] = None
        return

    # 若手勢不同，則重置
    if vars['current_gesture'] != number:
        vars['current_gesture'] = number
        vars['gesture_start_time'] = current_time
        return

    # 計算手勢持續時間
    gesture_duration = current_time - vars['gesture_start_time']
    # 將計秒文字縮小，並放置右下角
    text = f"Holding: {gesture_duration:.1f}s"
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
    position = (combined_image.shape[1] - text_size[0] - 10, combined_image.shape[0] - 10)
    cv2.putText(combined_image, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    if gesture_duration >= vars['gesture_hold_time'] and not vars['answered_current_question']:
        if number == vars['target_number']:
            # 提示正確
            vars['answer_feedback'] = "Correct!"
            vars['answered_current_question'] = True
        else:
            # 提示錯誤，不換題
            vars['answer_feedback'] = "Incorrect!"
            vars['wrong_answers'] += 1
            vars['total_wrong_answers'] += 1
            vars['consecutive_correct'] = 0  # 重置連續答對計數器

        vars['feedback_start_time'] = current_time  # 設置回饋訊息開始時間
        vars['feedback_active'] = True  # 暫停手勢偵測

# 第二階段: 左右手數字辨識階段
def number_recognition_phase(vars, hand_label, number, combined_image, instruction_images):
    if vars['stage_intro']:
        show_stage_intro(vars, combined_image)
        return

    if vars['number_recognition_sequence'] == []:
        # 建構題目順序，每張圖片都要出現一次，取設定的題目數量
        image_keys = [f"Left_{i}" for i in range(1, 6)] + [f"Right_{i}" for i in range(1, 6)]
        random.shuffle(image_keys)
        vars['number_recognition_sequence'] = image_keys[:vars['number_of_questions']]
        vars['number_recognition_index'] = 0
        vars['unanswered_questions'] = 0
        vars['correct_answers'] = 0
        vars['wrong_answers'] = 0
        vars['answered_current_question'] = False
        vars['consecutive_correct'] = 0
        vars['question_start_time'] = time.time()

    if vars['number_recognition_index'] >= len(vars['number_recognition_sequence']):
        # 記錄該階段的分數
        vars['stage_scores'][vars['stage']] = vars['score']
        vars['stage_wrong_answers'][vars['stage']] = vars['wrong_answers']
        vars['stage_unanswered'][vars['stage']] = vars['unanswered_questions']
        vars['stage_times'][vars['stage']] = int(time.time() - vars['stage_start_time'])
        # 計算階段花費時間
        vars['phase_time_spent'] = time.time() - vars['stage_start_time']
        # 結束階段，進入下一階段
        vars['stage'] += 1
        vars['stage_intro'] = True
        vars['number_recognition_sequence'] = []
        vars['stage_start_time'] = time.time()
        return

    # 獲取當前題目
    image_key = vars['number_recognition_sequence'][vars['number_recognition_index']]
    expected_hand, expected_number = image_key.split('_')
    expected_number = int(expected_number)

    # 顯示提示圖片
    instruction_image = instruction_images.get(image_key)
    if instruction_image is not None:
        instruction_image_resized = cv2.resize(
            instruction_image,
            (combined_image.shape[1] // 4, combined_image.shape[0] // 4)
        )
        x_offset = 10
        y_offset = 10
        combined_image[
            y_offset:y_offset + instruction_image_resized.shape[0],
            x_offset:x_offset + instruction_image_resized.shape[1]
        ] = instruction_image_resized
    else:
        draw_text(combined_image, f"Show {expected_number} with {expected_hand} Hand", (10, 40), 1, (255, 255, 255), 2)

    current_time = time.time()

    # 檢查是否超過設定的回答時間或已回答
    if current_time - vars['question_start_time'] >= vars['question_max_wait'] or vars['answered_current_question']:
        if not vars['answered_current_question']:
            vars['unanswered_questions'] += 1
            vars['consecutive_correct'] = 0
        vars['number_recognition_index'] += 1
        vars['question_start_time'] = time.time()
        vars['gesture_start_time'] = None
        vars['current_gesture'] = None
        vars['answered_current_question'] = False
        return

    if hand_label is None or number is None:
        vars['gesture_start_time'] = None
        vars['current_gesture'] = None
        return

    if hand_label != expected_hand:
        vars['gesture_start_time'] = None
        vars['current_gesture'] = None
        return

    # 如果當前手勢不同，重置計時器
    if vars['current_gesture'] != number:
        vars['current_gesture'] = number
        vars['gesture_start_time'] = current_time
        return

    # 計算手勢持續時間
    gesture_duration = current_time - vars['gesture_start_time']
    # 將計秒文字縮小，放置右下角
    text = f"Holding: {gesture_duration:.1f}s"
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
    position = (combined_image.shape[1] - text_size[0] - 10, combined_image.shape[0] - 10)
    cv2.putText(combined_image, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    if gesture_duration >= vars['gesture_hold_time'] and not vars['answered_current_question']:
        if number == expected_number:
            vars['correct_answers'] += 1
            vars['total_correct_answers'] += 1
            vars['score'] += vars['score_correct']
            vars['consecutive_correct'] += 1
            # 連續答對獎勵
            if vars['consecutive_correct'] == 3 or vars['consecutive_correct'] == 10:
                vars['score'] += vars['score_correct']  # 額外加分
            vars['answered_current_question'] = True
        else:
            vars['wrong_answers'] += 1
            vars['total_wrong_answers'] += 1
            vars['consecutive_correct'] = 0  # 重置連續答對計數器
            # 檢查錯誤次數是否達到設定的閾值
            if vars['wrong_answers'] >= vars['fail_threshold']:
                game_over(vars)
                return

        vars['gesture_start_time'] = None  # 重置計時器
        vars['current_gesture'] = None

    # 顯示統計數據（縮小字體）
    elapsed_time = int(time.time() - vars['stage_start_time'])
    draw_text(
        combined_image,
        f"Score: {vars['score']}  Wrong: {vars['wrong_answers']}  Unanswered: {vars['unanswered_questions']}  Time: {elapsed_time}s",
        (10, combined_image.shape[0] - 20),
        0.6,
        (255, 255, 255),
        1
    )