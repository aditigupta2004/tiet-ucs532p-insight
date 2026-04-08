from preprocess import Preprocessor
import cv2
from background_subtraction import BackgroundSubtractor
import json
import numpy as np

cap = cv2.VideoCapture("videos/video1.mp4")
preprocessor = Preprocessor()
bg_subtractor = BackgroundSubtractor()

cv2.namedWindow("Original", cv2.WINDOW_NORMAL)
cv2.namedWindow("Processed", cv2.WINDOW_NORMAL)
cv2.namedWindow("Reference Frames", cv2.WINDOW_NORMAL)
cv2.namedWindow("Diff View", cv2.WINDOW_NORMAL)

cv2.resizeWindow("Original", 600, 400)
cv2.resizeWindow("Processed", 600, 400)
cv2.resizeWindow("Reference Frames", 600, 400)
cv2.resizeWindow("Diff View", 600, 400)

# ── Load slots ────────────────────────────────────────────────────────────────
with open("slots.json", "r") as f:
    slots = json.load(f)

print(f"Loaded {len(slots)} slots")

DIFF_THRESHOLD = 30
OCCUPANCY_RATIO = 0.25

# ── Capture empty reference frames ───────────────────────────────────────────
ret, first_frame = cap.read()
if not ret:
    print("Error loading video")
    exit()

first_processed = preprocessor.process(first_frame)

slot_references = {}
for i, slot in enumerate(slots):
    if slot["occupied"] == 0:
        slot_references[i] = first_processed.copy()
    else:
        slot_references[i] = None

cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

frame_count = 0


def build_slot_grid(base_frame, slots, data_per_slot, color_fn, label_fn):
    """
    Renders a grid of per-slot image crops onto a black canvas.

    base_frame  : used only for bounding-rect extraction when crop source is a
                  processed (single-channel) image that lacks spatial metadata.
    data_per_slot : dict {slot_index: image | None}
    color_fn    : fn(slot_index) -> BGR border colour tuple
    label_fn    : fn(slot_index) -> label string
    """
    if not slots:
        return np.zeros((120, 160, 3), dtype=np.uint8)

    n = len(slots)
    cols = min(n, 4)
    rows = (n + cols - 1) // cols

    cell_w, cell_h = 160, 120
    pad = 6
    canvas = np.zeros((rows * (cell_h + pad) + pad,
                       cols * (cell_w + pad) + pad, 3), dtype=np.uint8)

    for i, slot in enumerate(slots):
        pts = np.array(slot["points"], np.int32)
        x, y, w, h = cv2.boundingRect(pts)

        # Clamp to base_frame bounds
        x = max(0, x)
        y = max(0, y)
        w = min(w, base_frame.shape[1] - x)
        h = min(h, base_frame.shape[0] - y)

        src = data_per_slot.get(i)

        if src is None or w <= 0 or h <= 0:
            cell = np.zeros((cell_h, cell_w, 3), dtype=np.uint8)
            cv2.putText(cell, "No ref yet", (8, cell_h // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (80, 80, 80), 1)
        else:
            # Normalise to BGR
            if len(src.shape) == 2:
                src_bgr = cv2.cvtColor(src, cv2.COLOR_GRAY2BGR)
            else:
                src_bgr = src.copy()

            crop = cv2.resize(src_bgr[y:y + h, x:x + w], (cell_w, cell_h))
            cell = crop

        row_idx = i // cols
        col_idx = i % cols
        cx = pad + col_idx * (cell_w + pad)
        cy = pad + row_idx * (cell_h + pad)

        # Border colour reflects current slot state
        cv2.rectangle(canvas, (cx - 2, cy - 2),
                      (cx + cell_w + 2, cy + cell_h + 2), color_fn(i), 2)
        canvas[cy:cy + cell_h, cx:cx + cell_w] = cell

        cv2.putText(canvas, label_fn(i), (cx + 4, cy + cell_h - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (210, 210, 210), 1, cv2.LINE_AA)

    return canvas


while True:
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    processed = preprocessor.process(frame)
    frame_count += 1

    occupied_count = 0
    ref_images = {}   # slot_index -> reference image (or None)
    diff_images = {}  # slot_index -> amplified diff image (or None)

    for i, slot in enumerate(slots):
        pts = np.array(slot["points"], np.int32)

        mask = np.zeros(processed.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)
        slot_area = np.sum(mask > 0)

        ref_images[i] = slot_references[i]

        if slot_references[i] is not None:
            diff = cv2.absdiff(processed, slot_references[i])
            diff_masked = cv2.bitwise_and(diff, diff, mask=mask)

            # Amplify diff 4x so small changes are clearly visible
            diff_amplified = cv2.convertScaleAbs(diff_masked, alpha=4.0)
            diff_images[i] = diff_amplified

            changed_pixels = np.sum(diff_masked > DIFF_THRESHOLD)
            ratio = changed_pixels / (slot_area + 1)
            is_occupied = ratio > OCCUPANCY_RATIO
        else:
            diff_images[i] = None
            is_occupied = bool(slot["occupied"])

        # Car just left → capture fresh empty reference
        if not is_occupied and slot["occupied"] == 1:
            slot_references[i] = processed.copy()
            ref_images[i] = slot_references[i]
            print(f"[Frame {frame_count}] Slot {i + 1} freed — reference updated")

        slots[i]["occupied"] = 1 if is_occupied else 0

        color = (0, 0, 255) if is_occupied else (0, 255, 0)
        cv2.polylines(frame, [pts], True, color, 2)
        center = pts.mean(axis=0).astype(int)
        cv2.putText(frame, f"#{i + 1}", tuple(center),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

        if is_occupied:
            occupied_count += 1

    # ── Reference frames window ───────────────────────────────────────────────
    # Shows the stored "empty" snapshot for each slot.
    # Border: green = currently free, red = currently occupied.
    # When a car leaves the reference updates live — you'll see it change here.
    ref_grid = build_slot_grid(
        first_processed,
        slots,
        ref_images,
        color_fn=lambda i: (0, 0, 255) if slots[i]["occupied"] else (0, 255, 0),
        label_fn=lambda i: f"#{i + 1} REF | {'OCC' if slots[i]['occupied'] else 'FREE'}"
    )
    cv2.imshow("Reference Frames", ref_grid)

    # ── Diff view window ──────────────────────────────────────────────────────
    # Shows per-slot pixel difference vs the reference (amplified 4x).
    # Bright = lots of change vs reference → occupied.
    # Dark = little change vs reference → empty / car still parked same spot.
    diff_grid = build_slot_grid(
        processed,
        slots,
        diff_images,
        color_fn=lambda i: (0, 100, 255) if slots[i]["occupied"] else (0, 200, 255),
        label_fn=lambda i: f"#{i + 1} DIFF | {'OCC' if slots[i]['occupied'] else 'FREE'}"
    )
    cv2.imshow("Diff View", diff_grid)

    # ── HUD ───────────────────────────────────────────────────────────────────
    free_count = len(slots) - occupied_count
    hud = f"Slots: {len(slots)}  |  Occupied: {occupied_count}  |  Free: {free_count}"
    font = cv2.FONT_HERSHEY_SIMPLEX
    (tw, th), _ = cv2.getTextSize(hud, font, 0.65, 2)
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (10 + tw + 20, 10 + th + 20), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    cv2.putText(frame, hud, (20, 10 + th + 10), font, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow("Original", frame)
    cv2.imshow("Processed", processed)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()