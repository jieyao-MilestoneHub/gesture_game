import time
import random
import cv2
from hand_gesture_app.phases.phase_common import show_stage_intro, game_over
from hand_gesture_app.utils.image_utils import draw_text

# 第六階段: Bonus階段
def bonus_phase(vars, hand_label, number, combined_image):
    if vars['stage_intro']:
        show_stage_intro(vars, combined_image)
        return
    
    # Bonus 階段在 vars['bonus_time'] 秒後結束
    elapsed_time = int(time.time() - vars['stage_start_time'])
    if elapsed_time >= vars['bonus_time']:
        vars['phase_time_spent'] = elapsed_time
        vars['stage_scores'][vars['stage']] = vars['score']  # 記錄 Bonus 階段的分數
        vars['stage_wrong_answers'][vars['stage']] = vars['wrong_answers']
        vars['stage_unanswered'][vars['stage']] = vars['unanswered_questions']
        vars['stage_times'][vars['stage']] = elapsed_time
        vars['stage'] = -2  # 遊戲勝利
        vars['game_end_time'] = time.time()
        return

    # **持續顯示 Score 和 Time**
    draw_text(
        combined_image,
        f"Score: {vars['score']}  Time: {elapsed_time}s",
        (10, combined_image.shape[0] - 20),
        0.6,
        (255, 255, 255),
        1
    )

    if vars['question'] == "":
        vars['target_number'] = random.randint(-15, 15)
        while vars['target_number'] == 0:
            vars['target_number'] = random.randint(-15, 15)
        vars['question'] = f"Reach the target number: {vars['target_number']}"
        vars['current_number'] = 0
        vars['question_start_time'] = time.time()
        vars['answered_current_question'] = False

    # 繪製題目與當前數字
    draw_text(combined_image, vars['question'], (10, 40), 1, (255, 255, 255), 2)
    draw_text(combined_image, f"Current Number: {vars['current_number']}", (10, 80), 1, (255, 255, 255), 2)

    if hand_label is None or number is None:
        vars['gesture_start_time'] = None
        vars['current_gesture'] = None
        return

    # 建立手勢識別的唯一標示
    gesture_id = (hand_label, number)

    # 若當前手勢與之前不同，重置計時器
    if vars['current_gesture'] != gesture_id:
        vars['current_gesture'] = gesture_id
        vars['gesture_start_time'] = current_time = time.time()
        return

    # 計算手勢持續時間
    gesture_duration = time.time() - vars['gesture_start_time']
    # 將計秒文字縮小，放置右下角
    text = f"Holding: {gesture_duration:.1f}s"
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
    position = (combined_image.shape[1] - text_size[0] - 10, combined_image.shape[0] - 10)
    cv2.putText(combined_image, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    if gesture_duration >= vars['gesture_hold_time']:
        if hand_label == 'Right':
            vars['current_number'] += number
        elif hand_label == 'Left':
            vars['current_number'] -= number

        vars['gesture_start_time'] = None  # 重置計時器
        vars['current_gesture'] = None

        # 檢查當前數字是否達到目標
        if vars['current_number'] == vars['target_number']:
            vars['correct_answers'] += 1
            vars['total_correct_answers'] += 1
            vars['score'] += vars['score_correct']
            vars['consecutive_correct'] += 1
            # 連續答對獎勵
            if vars['consecutive_correct'] == 3 or vars['consecutive_correct'] == 10:
                vars['score'] += vars['score_correct']  # 額外加分
            vars['question'] = ""
            vars['current_number'] = 0  # 重設當前數字
            vars['answered_current_question'] = True

    # 檢查錯誤次數是否達到設定的閾值
    if vars['wrong_answers'] >= vars['fail_threshold']:
        game_over(vars)
        return  # 立即退出函數