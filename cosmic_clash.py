import cv2
import mediapipe as mp
import random
import time
import math

# ---------------- COSMIC SETUP ----------------
cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ---------------- SPACE GAME VARIABLES ----------------
# STAR beats COMET
# COMET beats BLACK HOLE
# BLACK HOLE beats STAR

choices = ["STAR", "COMET", "BLACK HOLE"]

player_score = 0
cosmic_ai_score = 0

result_text = ""
ai_choice = ""

round_delay = 3
show_timer = False
timer_start = 0

# ---------------- COLORS ----------------
WHITE = (255, 255, 255)
CYAN = (255, 255, 0)
PURPLE = (255, 0, 255)
GOLD = (0, 215, 255)
RED = (0, 0, 255)
GREEN = (0, 255, 0)

# ---------------- STARS BACKGROUND ----------------
stars = []

for _ in range(100):
    stars.append([
        random.randint(0, 1280),
        random.randint(0, 720),
        random.randint(1, 3)
    ])

# ---------------- HELPER FUNCTIONS ----------------
def draw_space_background(frame):
    h, w, _ = frame.shape

    frame[:] = (5, 5, 20)

    for star in stars:
        x, y, size = star

        cv2.circle(frame, (x, y), size, WHITE, -1)

        # Move stars slowly
        star[1] += 1

        if star[1] > h:
            star[0] = random.randint(0, w)
            star[1] = 0


def fingers_up(hand):
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]

    fingers = []

    for tip, pip in zip(tips, pips):
        fingers.append(
            hand.landmark[tip].y < hand.landmark[pip].y
        )

    return fingers


def get_player_choice(fingers):

    # Closed fist = BLACK HOLE
    if fingers == [False, False, False, False]:
        return "BLACK HOLE"

    # Open hand = STAR
    elif fingers == [True, True, True, True]:
        return "STAR"

    # Two fingers = COMET
    elif fingers == [True, True, False, False]:
        return "COMET"

    return None


def get_winner(player, ai):

    if player == ai:
        return "DRAW"

    if (
        (player == "STAR" and ai == "COMET") or
        (player == "COMET" and ai == "BLACK HOLE") or
        (player == "BLACK HOLE" and ai == "STAR")
    ):
        return "PLAYER"

    return "AI"


# ---------------- MAIN LOOP ----------------
while True:

    success, camera = cap.read()

    if not success:
        break

    camera = cv2.flip(camera, 1)

    h, w, _ = camera.shape

    # Create space background
    frame = camera.copy()
    draw_space_background(frame)

    # Blend webcam + space
    frame = cv2.addWeighted(camera, 0.7, frame, 0.3, 0)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb)

    player_choice = None

    # ---------------- HAND DETECTION ----------------
    if results.multi_hand_landmarks:

        for hand in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS
            )

            fingers = fingers_up(hand)

            player_choice = get_player_choice(fingers)

            if player_choice and not show_timer:

                cv2.putText(
                    frame,
                    f"Your Cosmic Power: {player_choice}",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    CYAN,
                    2
                )

    current_time = time.time()

    # ---------------- TIMER ----------------
    if show_timer:

        elapsed = current_time - timer_start

        remaining = round_delay - int(elapsed)

        if remaining <= 0:

            show_timer = False
            result_text = ""
            ai_choice = ""

        else:

            cv2.putText(
                frame,
                f"Next Battle In: {remaining}",
                (700, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                GOLD,
                3
            )

    # ---------------- GAME LOGIC ----------------
    elif player_choice:

        ai_choice = random.choice(choices)

        winner = get_winner(player_choice, ai_choice)

        if winner == "PLAYER":

            player_score += 1
            result_text = "GALAXY SAVED!"

        elif winner == "AI":

            cosmic_ai_score += 1
            result_text = "COSMIC AI DOMINATES!"

        else:

            result_text = "SPACE-TIME DRAW!"

        show_timer = True
        timer_start = current_time

    # ---------------- TOP PANEL ----------------
    cv2.rectangle(frame, (0, 0), (w, 130), (0, 0, 0), -1)

    # Player score
    cv2.putText(
        frame,
        f"Explorer: {player_score}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        GREEN,
        2
    )

    # AI score
    cv2.putText(
        frame,
        f"Cosmic AI: {cosmic_ai_score}",
        (280, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        RED,
        2
    )

    # AI move
    if ai_choice:

        cv2.putText(
            frame,
            f"AI Power: {ai_choice}",
            (20, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            PURPLE,
            2
        )

    # Result
    if result_text:

        cv2.putText(
            frame,
            result_text,
            (500, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            GOLD,
            3
        )

    # Footer
    cv2.putText(
        frame,
        "STAR > COMET | COMET > BLACK HOLE | BLACK HOLE > STAR",
        (20, h - 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        WHITE,
        2
    )

    cv2.putText(
        frame,
        "Press Q to Exit the Universe",
        (20, h - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        CYAN,
        2
    )

    # Window name
    cv2.imshow("Cosmic Clash: Space Gesture Battle", frame)

    # Exit key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ---------------- CLEANUP ----------------
cap.release()
cv2.destroyAllWindows()
