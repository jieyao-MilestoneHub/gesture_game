import cv2

# 調整背景畫面
def darken_background(image, factor=0.5):
    return cv2.convertScaleAbs(image, alpha=factor, beta=0)

# 繪製文字
def draw_text(image, text, position, font_scale, color, thickness):
    cv2.putText(
        image,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        thickness
    )

# 繪製文字(居中)
def draw_text_centered(image, text, font_scale, color, thickness):
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
    text_x = (image.shape[1] - text_size[0]) // 2
    text_y = (image.shape[0] + text_size[1]) // 2
    cv2.putText(image, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)