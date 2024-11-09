
import cv2
import time
import numpy as np
from datetime import datetime
import os
import csv

from hand_gesture_app.config import initialize_variables
from hand_gesture_app.phases.phase_common import parameter_selection_screen
from hand_gesture_app.utils.file_utils import load_instruction_images
from hand_gesture_app.utils.image_utils import darken_background, draw_text_centered, draw_text
from hand_gesture_app.utils.drawing_utils import hands, draw_custom_hand_landmarks
from hand_gesture_app.gestures.gesture_recognition import calculate_hand_gesture, is_ok_gesture
from hand_gesture_app.phases.phase_free_test import free_testing_phase
from hand_gesture_app.phases.phase_number_test import number_testing_phase, number_recognition_phase
from hand_gesture_app.phases.phase_math_test import addition_phase, subtraction_phase, mixed_math_phase
from hand_gesture_app.phases.phase_bonus import bonus_phase
from hand_gesture_app.config import stage_names

# 主循環
def main():

    # 加載背景圖片
    background = cv2.imread("./hand_gesture_app/resources/images/background/image.png")
    if background is None:
        raise ValueError("背景圖片在指定路徑未找到。")

    vars = initialize_variables()
    parameter_selection_screen(vars)
    instruction_images = load_instruction_images()  # 加載提示圖片
    cap = cv2.VideoCapture(0)

    # 設定窗口名稱並設定全螢幕模式
    window_name = 'Hand Gesture Recognition'
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # 調整背景圖片大小
        background_resized = cv2.resize(background, (image.shape[1], image.shape[0]))

        # 翻轉攝像頭圖像成RGB
        image_rgb = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

        # 使用調暗的背景圖做為基底
        combined_image = darken_background(background_resized, factor=0.5)

        # 檢測手部
        results = hands.process(image_rgb)

        number = None
        hand_label = None
        ok_gesture_detected = False  # 用於檢測OK手勢

        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # 使用自定義函數繪製手部標記
                draw_custom_hand_landmarks(combined_image, hand_landmarks)
                hand_label = results.multi_handedness[idx].classification[0].label
                gesture_text = calculate_hand_gesture(
                    hand_landmarks.landmark, image.shape[1], image.shape[0]
                )

                number = int(gesture_text.replace("number ", "")) if "number" in gesture_text else None

                # 檢測OK手勢
                if is_ok_gesture(hand_landmarks.landmark, image.shape[1], image.shape[0]):
                    ok_gesture_detected = True

        # 根據不同階段進行處理
        if vars['stage'] == 0:
            free_testing_phase(vars, hand_label, number, combined_image)
        elif vars['stage'] == 1:
            number_testing_phase(vars, hand_label, number, combined_image)
        elif vars['stage'] == 2:
            number_recognition_phase(vars, hand_label, number, combined_image, instruction_images)
        elif vars['stage'] == 3:
            addition_phase(vars, hand_label, number, combined_image)
        elif vars['stage'] == 4:
            subtraction_phase(vars, hand_label, number, combined_image)
        elif vars['stage'] == 5:
            mixed_math_phase(vars, hand_label, number, combined_image)
        elif vars['stage'] == 6:
            bonus_phase(vars, hand_label, number, combined_image)
        else:
            # 遊戲結束或勝利
            if vars['game_end_time'] is None:
                vars['game_end_time'] = time.time()

            # 創建黑色背景
            stats_image = np.zeros_like(combined_image)

            # 顯示結果文字
            status_text = "You Win!" if vars['stage'] == -2 else "Game Over"
            draw_text_centered(stats_image, status_text, 2, (255, 255, 255), 3)

            # 計算已經顯示的時間
            elapsed_time = time.time() - vars['game_end_time']

            if elapsed_time >= 3:
                # 顯示統計數據
                stats_image = np.zeros_like(combined_image)  # 清空畫面
                total_score = sum(vars['stage_scores'].values())
                total_wrong = sum(vars['stage_wrong_answers'].values())
                total_unanswered = sum(vars['stage_unanswered'].values())
                total_time = sum(vars['stage_times'].values())

                # 建立表格資料
                stats_lines = []
                stats_lines.append(['Stage', 'Score', 'Wrong', 'Unanswered', 'Time'])
                for stage_num in range(2, 7):
                    score = vars['stage_scores'].get(stage_num, 0)
                    wrong = vars['stage_wrong_answers'].get(stage_num, 0)
                    unanswered = vars['stage_unanswered'].get(stage_num, 0)
                    time_spent = vars['stage_times'].get(stage_num, 0)
                    stage_name = stage_names[stage_num].replace("Stage", "")
                    stats_lines.append([stage_name, str(score), str(wrong), str(unanswered), str(time_spent)])

                stats_lines.append(['Total', str(total_score), str(total_wrong), str(total_unanswered), str(total_time)])

                # 設置字體大小和間距
                font_scale = 0.7
                thickness = 1
                line_spacing = 30
                column_spacing = 20

                num_columns = len(stats_lines[0])
                column_widths = [0] * num_columns

                # 計算每列的最大寬度
                for line in stats_lines:
                    for i, text in enumerate(line):
                        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
                        if text_size[0] > column_widths[i]:
                            column_widths[i] = text_size[0]

                # 計算表格總寬度
                table_width = sum(column_widths) + (num_columns - 1) * column_spacing

                # 計算表格起始位置，使其居中
                start_x = (stats_image.shape[1] - table_width) // 2
                y_start = (stats_image.shape[0] - len(stats_lines) * line_spacing) // 2

                # 計算每列的X位置
                x_positions = []
                current_x = start_x
                for width in column_widths:
                    x_positions.append(current_x)
                    current_x += width + column_spacing

                # 繪製表格
                for i, line in enumerate(stats_lines):
                    y_position = y_start + i * line_spacing
                    for j, text in enumerate(line):
                        x = x_positions[j]
                        cv2.putText(stats_image, text, (x, y_position), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

                # 顯示分數板
                cv2.imshow(window_name, stats_image)

                # 持續顯示直到偵測到OK手勢
                if ok_gesture_detected:
                    # 保存分數到CSV文件
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    folder_name = f"history/Game_{timestamp}"
                    os.makedirs(folder_name, exist_ok=True)
                    csv_file_path = os.path.join(folder_name, "game_results.csv")
                    with open(csv_file_path, mode='w', newline='') as csvfile:
                        fieldnames = ['Stage', 'Score', 'Wrong', 'Unanswered', 'Time']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        for stage_num in range(2, 7):
                            writer.writerow({
                                'Stage': stage_names.get(stage_num, "Unknown Stage"),
                                'Score': vars['stage_scores'].get(stage_num, 0),
                                'Wrong': vars['stage_wrong_answers'].get(stage_num, 0),
                                'Unanswered': vars['stage_unanswered'].get(stage_num, 0),
                                'Time': vars['stage_times'].get(stage_num, 0)
                            })
                        # 總分行
                        writer.writerow({
                            'Stage': 'Total',
                            'Score': total_score,
                            'Wrong': total_wrong,
                            'Unanswered': total_unanswered,
                            'Time': total_time
                        })
                    cap.release()
                    cv2.destroyAllWindows()
                    return
            else:
                # 繼續顯示結果文字
                cv2.imshow(window_name, stats_image)

            if cv2.waitKey(5) & 0xFF == 27:
                break

            continue

        # 始終顯示統計數據（確保持續顯示）
        if vars['stage'] >= 2 and vars['stage'] != 6:
            elapsed_time = int(time.time() - vars['stage_start_time'])
            draw_text(
                combined_image,
                f"Score: {vars['score']}  Wrong: {vars['wrong_answers']}  Unanswered: {vars.get('unanswered_questions',0)}  Time: {elapsed_time}s",
                (10, combined_image.shape[0] - 20),
                0.6,
                (255, 255, 255),
                1
            )

        # 顯示合成圖像
        cv2.imshow(window_name, combined_image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
