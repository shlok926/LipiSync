# ocr_module.py — Image-based Braille OCR using OpenCV

import cv2
import numpy as np
from braille_maps import dots_to_braille_char

def detect_braille_from_image(image_path: str) -> tuple[str, str]:
    """
    Detects braille dot patterns from an image.
    Returns (braille_string, status_message).
    Works best on high-contrast printed braille images.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return '', 'Could not load image. Check file path.'

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = np.ones((3, 3), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return '', 'No braille dots detected. Try a clearer image.'

        dots = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 20:
                continue
            M = cv2.moments(cnt)
            if M['m00'] == 0:
                continue
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            (x, y, w, h) = cv2.boundingRect(cnt)
            aspect = w / h if h > 0 else 0
            if 0.5 < aspect < 2.0 and area < 5000:
                dots.append((cx, cy))

        if not dots:
            return '', 'No circular dots detected. Ensure the image shows clear braille dots.'

        dots.sort(key=lambda p: (p[1], p[0]))
        braille_string = _cluster_dots_to_cells(dots)

        if not braille_string:
            return '', 'Could not parse dot pattern into braille cells.'

        return braille_string, f'Detected {len(dots)} dots → {len(braille_string)} braille characters.'

    except Exception as e:
        return '', f'OCR Error: {str(e)}'


def _cluster_dots_to_cells(dots: list[tuple]) -> str:
    """
    Groups detected dot centroids into 6-dot braille cells.
    Assumes standard braille cell layout.
    """
    if not dots:
        return ''

    ys = sorted(set(p[1] for p in dots))
    row_thresh = _median_spacing(ys) * 0.6 if len(ys) > 1 else 20

    rows = []
    current_row = [dots[0]]
    for pt in dots[1:]:
        if abs(pt[1] - current_row[-1][1]) < row_thresh:
            current_row.append(pt)
        else:
            rows.append(sorted(current_row, key=lambda p: p[0]))
            current_row = [pt]
    rows.append(sorted(current_row, key=lambda p: p[0]))

    if len(rows) < 2:
        return ''

    xs = sorted(set(p[0] for p in dots))
    col_spacing = _median_spacing(xs) if len(xs) > 1 else 20
    cell_width = col_spacing * 2.5

    xs_row0 = [p[0] for p in rows[0]]
    if not xs_row0:
        return ''
    min_x = min(xs_row0)

    cells_count = max(1, round((max(xs_row0) - min_x) / cell_width) + 1)
    result = []

    for cell_idx in range(cells_count):
        cell_x_start = min_x + cell_idx * cell_width
        cell_x_end = cell_x_start + cell_width

        active_dots = []
        row_positions = [1, 2, 3] if len(rows) >= 3 else [1, 2]

        for row_i, row in enumerate(rows[:3]):
            for pt in row:
                if cell_x_start <= pt[0] < cell_x_end:
                    left_half = (pt[0] - cell_x_start) < (cell_width / 2)
                    if left_half:
                        dot_num = row_positions[row_i] if row_i < len(row_positions) else row_i + 1
                    else:
                        dot_num = row_positions[row_i] + 3 if row_i < len(row_positions) else row_i + 4
                    active_dots.append(dot_num)

        if active_dots:
            result.append(dots_to_braille_char(active_dots))

    return ''.join(result)


def _median_spacing(values: list) -> float:
    if len(values) < 2:
        return 20
    diffs = [abs(values[i+1] - values[i]) for i in range(len(values)-1)]
    diffs.sort()
    return diffs[len(diffs)//2] or 20
