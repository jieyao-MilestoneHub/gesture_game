import time
import cv2
from hand_gesture_app.phases.phase_common import show_stage_intro, transition_to_next_stage, game_over
from hand_gesture_app.utils.math_utils import generate_question
from hand_gesture_app.utils.image_utils import draw_text

# 第三階段: 加法階段
def addition_phase(vars, hand_label, number, combined_image):
    math_phase(vars, hand_label, number, combined_image, 'add')

# 第四階段: 減法階段
def subtraction_phase(vars, hand_label, number, combined_image):
    math_phase(vars, hand_label, number, combined_image, 'subtract')

# 第五階段: 混合加減法階段
def mixed_math_phase(vars, hand_label, number, combined_image):
    math_phase(vars, hand_label, number, combined_image, 'mixed')

# 加減法階段的通用函數
def math_phase(vars, hand_label, number, combined_image, operation):
    if vars['stage_intro']:
        show_stage_intro(vars, combined_image)
        return

    # 初始化或重設問題
    if vars['question'] == "":
        vars['question'], vars['correct_answer'] = generate_question(operation)
        vars['question_start_time'] = time.time()
        vars['answered_current_question'] = False
        vars['attempted'] = False
        vars['question_index'] = vars.get('question_index', 0) + 1

    # 繪製題目
    draw_text(combined_image, f"Question: {vars['question']}", (10, 40), 1, (255, 255, 255), 2)

    current_time = time.time()

    # 結束條件：每題限時設定的時間
    if current_time - vars['question_start_time'] >= vars['question_max_wait'] or vars['answered_current_question']:
        if not vars['answered_current_question']:
            vars['unanswered_questions'] += 1
            vars['consecutive_correct'] = 0
        vars['question'] = ""
        vars['gesture_start_time'] = None
        vars['current_gesture'] = None
        vars['answered_current_question'] = False
        vars['attempted'] = False
        # 檢查是否已達到指定題數
        if vars['question_index'] >= vars['number_of_questions']:
            transition_to_next_stage(vars, current_time)
        return

    if number is None or hand_label is None:
        vars['gesture_start_time'] = None
        vars['current_gesture'] = None
        return

    # 建構玩家輸入值，根據手的方向
    player_answer = -number if hand_label == 'Left' else number

    # 若當前手勢與之前不同，重置計時器
    if vars['current_gesture'] != (hand_label, number):
        vars['current_gesture'] = (hand_label, number)
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
        if player_answer == vars['correct_answer']:
            vars['correct_answers'] += 1
            vars['total_correct_answers'] += 1
            vars['score'] += vars['score_correct']
            vars['consecutive_correct'] += 1
            # 連續答對獎勵
            if vars['consecutive_correct'] == 3 or vars['consecutive_correct'] == 10:
                vars['score'] += vars['score_correct']  # 額外加分
            vars['question'] = ""
            vars['answered_current_question'] = True
            vars['gesture_start_time'] = None
            vars['current_gesture'] = None
            # 如果達到題目上限，結束該階段
            if vars['question_index'] >= vars['number_of_questions']:
                transition_to_next_stage(vars, current_time)
        else:
            if not vars.get('attempted', False):
                vars['wrong_answers'] += 1
                vars['total_wrong_answers'] += 1
                vars['consecutive_correct'] = 0  # 重置連續答對計數器
                vars['attempted'] = True  # 標記已嘗試過，避免重複計算錯誤次數
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