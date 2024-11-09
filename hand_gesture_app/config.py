import time

# 初始化變量
def initialize_variables():
    return {
        'question_duration': 5,              # 自由測試階段持續時間
        'fail_threshold': 10,                # 每階段最多允許的錯誤次數
        'number_of_questions': 3,            # 每個階段的題目數量（除了加分階段）
        'score_correct': 1,                  # 答對一題加給分
        'question_max_wait': 7,              # 每題的回答時間
        'stage': 0,
        'correct_answers': 0,
        'wrong_answers': 0,
        'question': "",
        'correct_answer': 0,
        'start_time': time.time(),
        'last_gesture_time': None,
        'current_gesture': None,
        'last_operation_time': time.time(),
        'total_questions': 0,
        'score': 0,
        'waiting_for_new_gesture': False,
        'gesture_start_time': None,
        'gesture_hold_time': 1,
        'stage_intro': True,
        'stage_intro_start_time': None,
        'last_recognized_number': None,
        'total_correct_answers': 0,
        'total_wrong_answers': 0,
        'total_time_spent': 0,
        'stage_start_time': time.time(),
        'game_end_time': None,
        'current_number': 0,
        'target_number': 0,
        'attempts': 0,
        'max_attempts': 5,
        'number_recognition_sequence': [],  # 紀錄左右手判斷的題目順序
        'number_recognition_index': 0,      # 紀錄當前題目索引
        'consecutive_correct': 0,           # 連續答對的計數器
        'unanswered_questions': 0,          # 未回答的題數
        'answer_feedback': "",              # 回饋訊息
        'feedback_start_time': None,        # 回饋訊息開始時間
        'question_start_time': None,        # 每道題目的開始時間
        'answered_current_question': False, # 是否已回答當前題目
        'phase_time_spent': 0,              # 每個階段的總耗時
        'stage_scores': {},                 # 每個階段的分數記錄
        'stage_wrong_answers': {},          # 每個階段的錯誤次數
        'stage_unanswered': {},             # 每個階段的未回答次數
        'stage_times': {},                  # 每個階段的時間記錄
        'bonus_time': 100                   # Bonus 階段持續時間
    }

# 重置階段變量
def reset_stage_variables(vars):
    vars['question'] = ""
    vars['gesture_start_time'] = None
    vars['current_gesture'] = None
    vars['answered_current_question'] = False
    vars['attempted'] = False
    vars['question_index'] = 0
    vars['correct_answers'] = 0
    vars['wrong_answers'] = 0
    vars['unanswered_questions'] = 0
    vars['consecutive_correct'] = 0
    vars['current_number'] = 0
    vars['target_number'] = 0
    vars['number_recognition_sequence'] = []
    vars['number_recognition_index'] = 0


# 階段名稱
stage_names = {
    0: "Free Testing Stage",           # 30秒自由時間
    1: "Number Testing Stage",         # 符合給出的數字
    2: "Number Recognition Stage",     # 符合給出的圖片手勢
    3: "Addition Stage",               # 加法題目，答案在1到5之間
    4: "Subtraction Stage",            # 減法題目，答案在-5到5之間
    5: "Mixed Math Stage",             # 加減法混合題目
    6: "Bonus Stage"                   # 拼湊出隨機目標數，數字在-15到15之間
}