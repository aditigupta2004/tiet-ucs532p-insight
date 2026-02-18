import cv2
import json

slots = []
current_slot = []

def click_event(event, x, y, flags, param):
    global current_slot, slots, frame_copy

    if event == cv2.EVENT_LBUTTONDOWN:
        current_slot.append((x, y))

        # Draw point
        cv2.circle(frame_copy, (x, y), 5, (0, 0, 255), -1)

        # Draw line
        if len(current_slot) > 1:
            cv2.line(frame_copy, current_slot[-2], current_slot[-1], (255, 0, 0), 2)

        # If 4 points → save slot
        if len(current_slot) == 4:
            slots.append(current_slot.copy())

            # Close polygon
            cv2.line(frame_copy, current_slot[-1], current_slot[0], (255, 0, 0), 2)

            print(f"Slot {len(slots)} added: {current_slot}")
            current_slot = []

# Load video
cap = cv2.VideoCapture("videos/video1.mp4")

ret, frame = cap.read()
cap.release()

frame_copy = frame.copy()

cv2.namedWindow("Annotate Slots")
cv2.setMouseCallback("Annotate Slots", click_event)

while True:
    cv2.imshow("Annotate Slots", frame_copy)

    key = cv2.waitKey(1) & 0xFF

    # Press 's' to save
    if key == ord('s'):
        with open("slots.json", "w") as f:
            json.dump(slots, f)
        print("Slots saved to slots.json")

    # Press 'r' to reset
    elif key == ord('r'):
        frame_copy = frame.copy()
        slots = []
        current_slot = []
        print("Reset")

    # Press 'q' to quit
    elif key == ord('q'):
        break

cv2.destroyAllWindows()
