# Coin Collector

A simple 2D grid game built with Streamlit. Move the player to collect all coins on the grid.

## Run

```bash
# From the project folder
python -m pip install -r requirements.txt
streamlit run app.py
```

## Controls

- Up: Move up
- Left: Move left
- Right: Move right
- Down: Move down
- Reset: Generate a new layout
 - Keyboard: Click the invisible input at the top, then use WASD

## Notes

- Game state persists across interactions via `st.session_state`.
- Coins are placed randomly each reset; player starts in the center.
 - You can upload a custom PNG for coin appearance in the sidebar.
 - Place custom images in `assets/` to customize visuals:
	 - `assets/coin.png`: coin image (optional; falls back to built-in)
	 - `assets/player.png`: player image (optional)
	 - `assets/obstacle.png`: obstacle image (optional)
 - Hitting an obstacle ends the game (Lost). Collect all coins to win.
