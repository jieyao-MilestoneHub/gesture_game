import time
import numpy as np
import cv2
from hand_gesture_app.config import stage_names, reset_stage_variables
from hand_gesture_app.utils.image_utils import draw_text_centered

# 顯示階段介紹
def show_stage_intro(vars, combined_image):
    if vars['stage'] in stage_names:
        stage_name = stage_names[vars['stage']]
    else:
        stage_name = "Unknown Stage"

    # 計算階段介紹的持續時間
    if vars['stage_intro_start_time'] is None:
        vars['stage_intro_start_time'] = time.time()
    
    elapsed_time = time.time() - vars['stage_intro_start_time']

    # 設定漸層出現時間為2秒
    duration = 2.0  
    max_length = len(stage_name)
    
    # 計算要顯示的字母數量
    if elapsed_time < duration:
        letters_to_show = int((elapsed_time / duration) * max_length)
        display_text = stage_name[:letters_to_show]
    else:
        display_text = stage_name

    # 顯示漸層效果的文字
    draw_text_centered(combined_image, display_text, 1, (255, 255, 255), 3)

    # 完整顯示5秒後自動結束階段介紹
    if elapsed_time >= 5:
        vars['stage_intro'] = False
        vars['stage_intro_start_time'] = None  # 重設計時器
        vars['stage_start_time'] = time.time()  # 紀錄階段開始時間
        vars['phase_time_spent'] = 0  # 重置階段總耗時
        vars['score'] = 0  # 重置分數
        vars['wrong_answers'] = 0  # 重置錯誤次數
        vars['unanswered_questions'] = 0  # 重置未回答題數
        vars['consecutive_correct'] = 0  # 重置連續答對計數器
        vars['total_time_spent'] = 0  # 重置總耗時
        reset_stage_variables(vars)   # 重置階段變量

# 參數選擇介面
def parameter_selection_screen(vars):
    # 定義參數列表
    parameters = [
        {
            'name': 'question_duration', 
            'display_name': 'Free test time (seconds)', 
            'value': vars['question_duration'], 
            'default': 5, 
            'min': 1, 
            'max': 60
        },
        {
            'name': 'fail_threshold', 
            'display_name': 'Max errors allowed per stage', 
            'value': vars['fail_threshold'], 
            'default': 10, 
            'min': 1, 
            'max': 100
        },
        {
            'name': 'number_of_questions', 
            'display_name': 'Number of questions per stage', 
            'value': vars['number_of_questions'], 
            'default': 3, 
            'min': 1, 
            'max': 100
        },
        {
            'name': 'score_correct', 
            'display_name': 'Score for each correct answer', 
            'value': vars['score_correct'], 
            'default': 1, 
            'min': 1, 
            'max': 100
        },
        {
            'name': 'question_max_wait', 
            'display_name': 'Response time per question (seconds)', 
            'value': vars['question_max_wait'], 
            'default': 7, 
            'min': 1, 
            'max': 60
        },
        {
            'name': 'bonus_time', 
            'display_name': 'Bonus stage time (seconds)', 
            'value': vars['bonus_time'], 
            'default': 100, 
            'min': 1, 
            'max': 200
        }
    ]

    options = ['Return', 'Cancel', 'Confirm']

    current_selection_index = 0  # Start with first parameter

    while True:
        # Create a black image
        screen_height = 600
        screen_width = 800
        screen = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

        # Display the parameters
        y_start = 100
        y_offset = 40

        for idx, param in enumerate(parameters):
            y_pos = y_start + idx * y_offset
            color = (255, 255, 255)
            if idx == current_selection_index:
                color = (0, 255, 0)  # Highlight selected parameter

            text = f"{param['display_name']}: {param['value']}"
            cv2.putText(screen, text, (50, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Display options
        option_y_start = y_start + len(parameters) * y_offset + 50
        for idx, option in enumerate(options):
            y_pos = option_y_start + idx * y_offset
            color = (255, 255, 255)
            if len(parameters) + idx == current_selection_index:
                color = (0, 255, 0)  # Highlight selected option

            cv2.putText(screen, option, (50, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Display instructions
        instruction_text = "Using arrow keys to choose item and specify the number."
        cv2.putText(screen, instruction_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Show the screen
        cv2.imshow('Parameter Selection', screen)

        # Wait for key press
        key = cv2.waitKeyEx(0)

        # Handle key input
        if key == 27:  # ESC key to exit
            cv2.destroyWindow('Parameter Selection')
            exit()
        elif key == 13 or key == 10:  # Enter key
            if current_selection_index >= len(parameters):
                # Options selected
                selected_option = options[current_selection_index - len(parameters)]
                if selected_option == 'Confirm':
                    # Update vars with new values
                    for param in parameters:
                        vars[param['name']] = param['value']
                    cv2.destroyWindow('Parameter Selection')
                    return
                elif selected_option == 'Cancel':
                    cv2.destroyWindow('Parameter Selection')
                    exit()
                elif selected_option == 'Return':
                    # Set vars to default values
                    for param in parameters:
                        vars[param['name']] = param['default']
                    cv2.destroyWindow('Parameter Selection')
                    return
            else:
                # Do nothing on parameters
                pass
        elif key == 2490368:  # Up arrow key
            current_selection_index = (current_selection_index - 1) % (len(parameters) + len(options))
        elif key == 2621440:  # Down arrow key
            current_selection_index = (current_selection_index + 1) % (len(parameters) + len(options))
        elif key == 2424832:  # Left arrow key
            if current_selection_index < len(parameters):
                param = parameters[current_selection_index]
                param['value'] = max(param['min'], param['value'] - 1)
        elif key == 2555904:  # Right arrow key
            if current_selection_index < len(parameters):
                param = parameters[current_selection_index]
                param['value'] = min(param['max'], param['value'] + 1)
        else:
            # For testing, print the key code
            print(f"Key pressed: {key}")

# 過渡到下一階段的函數
def transition_to_next_stage(vars, current_time):
    # 記錄該階段的分數
    elapsed_time = int(current_time - vars['stage_start_time'])
    vars['stage_scores'][vars['stage']] = vars['score']
    vars['stage_wrong_answers'][vars['stage']] = vars['wrong_answers']
    vars['stage_unanswered'][vars['stage']] = vars['unanswered_questions']
    vars['stage_times'][vars['stage']] = elapsed_time
    vars['phase_time_spent'] = elapsed_time

    # 更新階段並進入介紹
    vars['stage'] += 1
    vars['stage_intro'] = True
    vars['question'] = ""
    vars['gesture_start_time'] = None
    vars['current_gesture'] = None
    vars['question_index'] = 0
    vars['correct_answers'] = 0
    vars['wrong_answers'] = 0
    vars['unanswered_questions'] = 0
    vars['consecutive_correct'] = 0
    vars['stage_start_time'] = time.time()
    reset_stage_variables(vars)  # 重置階段變量

def game_over(vars):
    current_time = time.time()
    elapsed_time = int(current_time - vars['stage_start_time'])
    vars['stage_scores'][vars['stage']] = vars['score']
    vars['stage_wrong_answers'][vars['stage']] = vars['wrong_answers']
    vars['stage_unanswered'][vars['stage']] = vars.get('unanswered_questions', 0)
    vars['stage_times'][vars['stage']] = elapsed_time
    vars['phase_time_spent'] = elapsed_time
    vars['stage'] = -1
    vars['game_end_time'] = current_time
