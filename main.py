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
cv2.resizeWindow("Original", 600, 400)
cv2.resizeWindow("Processed", 600, 400)

# ── Load slots ────────────────────────────────────────────────────────────────
with open("slots.json", "r") as f:
    slots = json.load(f)

print(f"Loaded {len(slots)} slots")

DIFF_THRESHOLD = 30     # pixel intensity difference to count as "changed"
OCCUPANCY_RATIO = 0.25  # 25% of slot pixels must differ to call it occupied

# ── Capture empty reference frames ───────────────────────────────────────────
# Strategy: use slots.json initial state to decide reference
# For slots marked empty (0) → capture reference from first frame
# For slots marked occupied (1) → reference will be set when car leaves

ret, first_frame = cap.read()
if not ret:
    print("Error loading video")
    exit()

first_processed = preprocessor.process(first_frame)

# Per-slot reference: stores the grayscale crop of the slot when it was last empty
slot_references = {}

for i, slot in enumerate(slots):
    if slot["occupied"] == 0:
        # Slot starts empty — use first frame as reference
        slot_references[i] = first_processed.copy()
    else:
        # Slot starts occupied — no empty reference yet, will update when freed
        slot_references[i] = None

# Reset to start
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    processed = preprocessor.process(frame)
    frame_count += 1

    occupied_count = 0

    for i, slot in enumerate(slots):
        pts = np.array(slot["points"], np.int32)

        # Build slot mask
        mask = np.zeros(processed.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)
        slot_area = np.sum(mask > 0)

        if slot_references[i] is not None:
            # Diff current frame against empty reference
            diff = cv2.absdiff(processed, slot_references[i])
            diff_masked = cv2.bitwise_and(diff, diff, mask=mask)

            changed_pixels = np.sum(diff_masked > DIFF_THRESHOLD)
            ratio = changed_pixels / (slot_area + 1)

            is_occupied = ratio > OCCUPANCY_RATIO
        else:
            # No reference yet — fall back to annotated state
            is_occupied = bool(slot["occupied"])

        # If slot is now detected as empty AND we previously thought it was occupied
        # → update the reference to current frame (car just left)
        if not is_occupied and slot["occupied"] == 1:
            slot_references[i] = processed.copy()
            print(f"[Frame {frame_count}] Slot {i + 1} freed — reference updated")

        slots[i]["occupied"] = 1 if is_occupied else 0

        # Draw
        color = (0, 0, 255) if is_occupied else (0, 255, 0)
        cv2.polylines(frame, [pts], True, color, 2)

        center = pts.mean(axis=0).astype(int)
        cv2.putText(frame, f"#{i + 1}", tuple(center),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

        if is_occupied:
            occupied_count += 1

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