import cv2
import json
import numpy as np

slots = []
current_slot = []
pending_confirmation = False  # Waiting for user to press 1 or 0

WINDOW_NAME = "Annotate Slots"


def draw_legend(frame):
    """Draw high-quality legend on top-right corner."""
    legend = [
        "Controls",
        "Left Click : Add Point (max 4)",
        "U : Undo Point",
        "D : Delete Last Slot",
        "R : Reset All",
        "S : Save Slots",
        "Q : Quit",
        "",
        "After 4 points:",
        "1 = Occupied (Red)",
        "0 = Empty (Green)",
    ]

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.55
    thickness = 1

    line_height = 24
    padding = 10

    max_width = 0
    for text in legend:
        (w, h), _ = cv2.getTextSize(text, font, font_scale, thickness)
        max_width = max(max_width, w)

    box_width = max_width + 2 * padding
    box_height = len(legend) * line_height + padding

    x = frame.shape[1] - box_width - 20
    y = 20

    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + box_width, y + box_height), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    for i, text in enumerate(legend):
        if not text:
            continue
        color = (200, 200, 200)
        if text.startswith("1 ="):
            color = (80, 80, 255)
        elif text.startswith("0 ="):
            color = (80, 255, 80)
        elif i == 0 or text.startswith("After"):
            color = (255, 255, 100)

        text_y = y + padding + (i + 1) * line_height - 5
        cv2.putText(frame, text, (x + padding, text_y),
                    font, font_scale, color, thickness, cv2.LINE_AA)


def draw_prompt_banner(frame):
    """Show a prominent banner asking for occupied/empty input."""
    text = "Is this slot OCCUPIED? Press  1 = Yes (Red)   0 = No (Green)"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    thickness = 2

    (w, h), _ = cv2.getTextSize(text, font, font_scale, thickness)
    padding = 14

    banner_x = (frame.shape[1] - w) // 2 - padding
    banner_y = frame.shape[0] - 60
    banner_w = w + 2 * padding
    banner_h = h + 2 * padding

    overlay = frame.copy()
    cv2.rectangle(overlay, (banner_x, banner_y),
                  (banner_x + banner_w, banner_y + banner_h), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

    cv2.rectangle(frame, (banner_x, banner_y),
                  (banner_x + banner_w, banner_y + banner_h), (0, 200, 255), 2)

    cv2.putText(frame, text,
                (banner_x + padding, banner_y + padding + h),
                font, font_scale, (0, 220, 255), thickness, cv2.LINE_AA)


def draw_slots(frame):
    """Draw all saved slots with their occupancy color."""
    for idx, slot in enumerate(slots):
        pts = np.array(slot["points"], np.int32)
        color = (0, 0, 255) if slot["occupied"] else (0, 255, 0)
        cv2.polylines(frame, [pts], True, color, 2)

        # Label each slot
        center = pts.mean(axis=0).astype(int)
        label = f"#{idx + 1}"
        cv2.putText(frame, label, tuple(center),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)


def draw_current_slot(frame):
    """Draw points being currently selected, auto-close on 4 points."""
    for i, point in enumerate(current_slot):
        cv2.circle(frame, point, 5, (0, 0, 255), -1)
        if i > 0:
            cv2.line(frame, current_slot[i - 1], point, (255, 255, 0), 2)

    # Auto-close: draw line from last point back to first
    if len(current_slot) == 4:
        cv2.line(frame, current_slot[3], current_slot[0], (255, 255, 0), 2)


def click_event(event, x, y, flags, param):
    global current_slot, slots, pending_confirmation

    if pending_confirmation:
        return  # Block clicks while waiting for 1/0 input

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(current_slot) < 4:
            current_slot.append((x, y))
            print(f"Point {len(current_slot)} added: ({x}, {y})")

            if len(current_slot) == 4:
                print("4 points placed — quadrilateral closed.")
                print("Press 1 if OCCUPIED, 0 if EMPTY.")
                pending_confirmation = True


# ── Load video frame ──────────────────────────────────────────────────────────
cap = cv2.VideoCapture("videos/video1.mp4")
ret, frame = cap.read()
cap.release()

if not ret:
    print("Error loading video")
    exit()

# ── Load existing slots ───────────────────────────────────────────────────────
try:
    with open("slots.json", "r") as f:
        slots = json.load(f)
    print(f"Loaded {len(slots)} existing slots")
except Exception:
    slots = []
    print("No existing slots found")

# ── Window setup ──────────────────────────────────────────────────────────────
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, 900, 600)
cv2.setMouseCallback(WINDOW_NAME, click_event)

while True:
    frame_copy = frame.copy()

    draw_slots(frame_copy)
    draw_current_slot(frame_copy)
    draw_legend(frame_copy)

    if pending_confirmation:
        draw_prompt_banner(frame_copy)

    cv2.imshow(WINDOW_NAME, frame_copy)

    key = cv2.waitKey(1) & 0xFF

    # ── Handle occupancy confirmation (1 or 0) ────────────────────────────────
    if pending_confirmation:
        if key == ord('1'):
            slots.append({"points": current_slot.copy(), "occupied": 1})
            print(f"Slot {len(slots)} added as OCCUPIED (Red)")
            current_slot = []
            pending_confirmation = False

        elif key == ord('0'):
            slots.append({"points": current_slot.copy(), "occupied": 0})
            print(f"Slot {len(slots)} added as EMPTY (Green)")
            current_slot = []
            pending_confirmation = False

        continue  # Skip all other keys while confirming

    # ── Normal controls ───────────────────────────────────────────────────────
    if key == ord('s'):
        with open("slots.json", "w") as f:
            json.dump(slots, f, indent=2)
        print(f"Saved {len(slots)} slots to slots.json")

    elif key == ord('r'):
        slots = []
        current_slot = []
        pending_confirmation = False
        print("Reset all slots")

    elif key == ord('u'):
        if current_slot:
            current_slot.pop()
            pending_confirmation = False
            print("Removed last point")

    elif key == ord('d'):
        if slots:
            removed = slots.pop()
            print(f"Deleted last slot (was {'occupied' if removed['occupied'] else 'empty'})")

    elif key == ord('q'):
        break

cv2.destroyAllWindows()