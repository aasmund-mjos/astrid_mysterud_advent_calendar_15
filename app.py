import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import random
from pathlib import Path
import time

GRID_W = 12
GRID_H = 12
CELL = 32
TIME_LIMIT =30

PLAYER_COLOR = (50, 220, 90)
COIN_COLOR = (255, 215, 0)
WALL_COLOR = (35, 40, 55)
BG_COLOR = (20, 22, 28)


def init_state():
    if "grid" not in st.session_state:
        st.session_state.grid = np.zeros((GRID_H, GRID_W), dtype=int)  # 0 empty, 1 coin
    if "player" not in st.session_state:
        st.session_state.player = [GRID_W // 2, GRID_H // 2]
    if "coins" not in st.session_state:
        # place coins randomly avoiding player start
        rng = random.Random(42)
        coins = set()
        while len(coins) < 10:
            x = rng.randrange(GRID_W)
            y = rng.randrange(GRID_H)
            if [x, y] != st.session_state.player:
                coins.add((x, y))
        st.session_state.coins = coins
    if "moves" not in st.session_state:
        st.session_state.moves = 0
    if "won" not in st.session_state:
        st.session_state.won = False
    if "lost" not in st.session_state:
        st.session_state.lost = False
    if "started" not in st.session_state:
        st.session_state.started = False
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "end_time" not in st.session_state:
        st.session_state.end_time = None
    if "lost_reason" not in st.session_state:
        st.session_state.lost_reason = None  # "obstacle" | "timeout" | None
    if "coin_image" not in st.session_state:
        # Load default coin image from assets; fallback to ellipse if missing
        assets_path = Path(__file__).parent / "assets" / "coin.png"
        if assets_path.exists():
            try:
                st.session_state.coin_image = Image.open(assets_path)
            except Exception:
                st.session_state.coin_image = None
        else:
            # Procedural default coin image (gold circle with shine)
            size = 64
            base = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            d = ImageDraw.Draw(base)
            d.ellipse([(4, 4), (size - 4, size - 4)], fill=(255, 215, 0, 255))
            d.ellipse([(12, 12), (size - 12, size - 12)], outline=(255, 240, 120, 255), width=2)
            d.polygon([(size*0.2, size*0.35), (size*0.5, size*0.2), (size*0.8, size*0.35)], fill=(255, 240, 160, 160))
            st.session_state.coin_image = base
    if "keybuf" not in st.session_state:
        st.session_state.keybuf = ""

    # Load custom player image if present
    if "player_image" not in st.session_state:
        p_path = Path(__file__).parent / "assets" / "player.png"
        if p_path.exists():
            try:
                st.session_state.player_image = Image.open(p_path).convert("RGBA")
            except Exception:
                st.session_state.player_image = None
        else:
            st.session_state.player_image = None

    # Place obstacles and load image
    if "obstacles" not in st.session_state:
        rng = random.Random(99)
        obstacles = set()
        target_count = 8
        while len(obstacles) < target_count:
            x = rng.randrange(GRID_W)
            y = rng.randrange(GRID_H)
            if [x, y] != st.session_state.player and (x, y) not in st.session_state.coins:
                obstacles.add((x, y))
        st.session_state.obstacles = obstacles
    if "obstacle_image" not in st.session_state:
        o_path = Path(__file__).parent / "assets" / "obstacle.png"
        if o_path.exists():
            try:
                st.session_state.obstacle_image = Image.open(o_path).convert("RGBA")
            except Exception:
                st.session_state.obstacle_image = None
        else:
            st.session_state.obstacle_image = None


def reset():
    st.session_state.grid = np.zeros((GRID_H, GRID_W), dtype=int)
    st.session_state.player = [GRID_W // 2, GRID_H // 2]
    rng = random.Random()  # new seed each run
    coins = set()
    while len(coins) < 10:
        x = rng.randrange(GRID_W)
        y = rng.randrange(GRID_H)
        if [x, y] != st.session_state.player:
            coins.add((x, y))
    st.session_state.coins = coins
    st.session_state.moves = 0
    st.session_state.won = False
    st.session_state.lost = False
    st.session_state.started = False
    st.session_state.start_time = None
    st.session_state.end_time = None
    st.session_state.lost_reason = None
    # regenerate obstacles
    rng = random.Random()
    obstacles = set()
    target_count = 8
    while len(obstacles) < target_count:
        x = rng.randrange(GRID_W)
        y = rng.randrange(GRID_H)
        if [x, y] != st.session_state.player and (x, y) not in st.session_state.coins:
            obstacles.add((x, y))
    st.session_state.obstacles = obstacles


def move(dx, dy):
    if not st.session_state.started or st.session_state.won or st.session_state.lost:
        return
    x, y = st.session_state.player
    nx, ny = x + dx, y + dy
    if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
        st.session_state.player = [nx, ny]
        st.session_state.moves += 1
        # collect coin if present
        if (nx, ny) in st.session_state.coins:
            st.session_state.coins.remove((nx, ny))
        if not st.session_state.coins:
            st.session_state.won = True
            if st.session_state.end_time is None:
                st.session_state.end_time = time.time()
        # collision with obstacle loses the game
        if (nx, ny) in st.session_state.obstacles:
            st.session_state.lost = True
            if st.session_state.end_time is None:
                st.session_state.end_time = time.time()
            st.session_state.lost_reason = "obstacle"


def _format_time(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"


def handle_key():
    raw = st.session_state.get("keybuf", "")
    if not raw:
        return
    ch = raw.strip().lower()
    if ch == "w":
        move(0, -1)
    elif ch == "s":
        move(0, 1)
    elif ch == "a":
        move(-1, 0)
    elif ch == "d":
        move(1, 0)
    # clear buffer to accept next key
    st.session_state.keybuf = ""


def render():
    img = Image.new("RGB", (GRID_W * CELL, GRID_H * CELL), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Grid
    for x in range(GRID_W + 1):
        draw.line([(x * CELL, 0), (x * CELL, GRID_H * CELL)], fill=WALL_COLOR)
    for y in range(GRID_H + 1):
        draw.line([(0, y * CELL), (GRID_W * CELL, y * CELL)], fill=WALL_COLOR)

    # Coins (custom image if provided, else ellipse)
    for (cx, cy) in st.session_state.coins:
        pad = 6
        if st.session_state.coin_image is not None:
            # Resize with aspect fit into cell
            target_size = CELL - 2 * pad
            coin_img = st.session_state.coin_image.copy()
            coin_img = coin_img.convert("RGBA")
            coin_img = coin_img.resize((target_size, target_size), resample=Image.LANCZOS)
            img.paste(
                coin_img,
                (cx * CELL + pad, cy * CELL + pad),
                mask=coin_img,
            )
        else:
            draw.ellipse(
                [
                    (cx * CELL + pad, cy * CELL + pad),
                    (cx * CELL + CELL - pad, cy * CELL + CELL - pad),
                ],
                fill=COIN_COLOR,
            )

    # Obstacles
    for (ox, oy) in st.session_state.obstacles:
        pad = 4
        if st.session_state.obstacle_image is not None:
            target = CELL - 2 * pad
            oimg = st.session_state.obstacle_image.copy()
            oimg = oimg.resize((target, target), resample=Image.LANCZOS)
            img.paste(oimg, (ox * CELL + pad, oy * CELL + pad), mask=oimg)
        else:
            draw.rectangle(
                [
                    (ox * CELL + pad, oy * CELL + pad),
                    (ox * CELL + CELL - pad, oy * CELL + CELL - pad),
                ],
                fill=(200, 60, 60),
            )

    # Player
    px, py = st.session_state.player
    pad = 4
    if st.session_state.player_image is not None:
        target = CELL - 2 * pad
        pimg = st.session_state.player_image.copy()
        pimg = pimg.resize((target, target), resample=Image.LANCZOS)
        img.paste(pimg, (px * CELL + pad, py * CELL + pad), mask=pimg)
    else:
        draw.rectangle(
            [
                (px * CELL + pad, py * CELL + pad),
                (px * CELL + CELL - pad, py * CELL + CELL - pad),
            ],
            fill=PLAYER_COLOR,
        )

    return img


def main():
    st.set_page_config(page_title="Christmas Calendar", page_icon="assets/coin.png", layout="centered")
    st.title("Astrids Online Advent Calendar")
    st.caption("""Oh Noo! Avoid getting a B, whilst you collect all the A's! You have to be quick though, as time is ticking!
I'm sorry, when I uploaded the app, it got very laggy, so don't spam buttons please :)""")

    init_state()

    # Auto-refresh to keep countdown updating
    ar = getattr(st, "autorefresh", None)
    if callable(ar):
        ar(interval=300, key="countdown_refresh", limit=None)
    else:
        ear = getattr(st, "experimental_autorefresh", None)
        if callable(ear):
            ear(interval=300, key="countdown_refresh", limit=100000)

    # Countdown timer (20s) with auto-fail on timeout
    now = time.time()
    if st.session_state.started and st.session_state.start_time is not None:
        end_ref = st.session_state.end_time or (st.session_state.start_time + TIME_LIMIT)
        remaining = max(0.0, end_ref - now) if not (st.session_state.won or st.session_state.lost) else max(0.0, (st.session_state.start_time + TIME_LIMIT) - (st.session_state.end_time or now))
    else:
        # not started yet
        remaining = float(TIME_LIMIT)

    if st.session_state.started and not st.session_state.won and not st.session_state.lost:
        # if time exceeded, mark as lost (timeout)
        if st.session_state.start_time is not None and now - st.session_state.start_time >= TIME_LIMIT:
            st.session_state.lost = True
            st.session_state.lost_reason = "timeout"
            if st.session_state.end_time is None:
                st.session_state.end_time = st.session_state.start_time + TIME_LIMIT
            remaining = 0.0

    tcol = st.columns([1, 2, 1])[1]
    with tcol:
        st.metric("Time left", _format_time(remaining))

    # Layout: game on left, compact controls on right
    board_col, ctrl_col = st.columns([5, 2])

    # Controls (compact arrow layout)
    with ctrl_col:
        if not st.session_state.started and not (st.session_state.won or st.session_state.lost):
            if st.button("▶️ Start", use_container_width=True, key="btn_start"):
                st.session_state.started = True
                st.session_state.start_time = time.time()
                st.session_state.end_time = None
                st.rerun()

        row1 = st.columns([1, 1, 1])
        if row1[1].button("⬆️", use_container_width=True, key="btn_up"):
            move(0, -1)

        row2 = st.columns([1, 1, 1])
        if row2[0].button("⬅️", use_container_width=True, key="btn_left"):
            move(-1, 0)
        if row2[2].button("➡️", use_container_width=True, key="btn_right"):
            move(1, 0)

        row3 = st.columns([1, 1, 1])
        if row3[1].button("⬇️", use_container_width=True, key="btn_down"):
            move(0, 1)

        st.divider()
        if st.button("🔁 Reset", use_container_width=True, key="btn_reset"):
            reset()
            st.rerun()

    # Render board after handling input
    with board_col:
        img = render()
        st.image(img)

    if st.session_state.won:
        st.success("Wii, you are a beast! Straight A's for you! 🏆")
    if st.session_state.lost:
        if st.session_state.lost_reason == "timeout":
            st.error("Time's up! Good try Astrid!")
        else:
            st.error("OH NOOO, you got a B! :((")


if __name__ == "__main__":
    main()

