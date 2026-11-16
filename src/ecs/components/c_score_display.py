class CScoreDisplay:

    def __init__(
        self,
        right_x: float,
        center_y: float,
        font_path: str,
        text_size: int,
        text_color,
        initial_value: int = 0,
        tracks_score: bool = True,
    ) -> None:
        self.value = initial_value
        self.tracks_score = tracks_score
        self.right_x = right_x
        self.center_y = center_y
        self.font_path = font_path
        self.text_size = text_size
        self.text_color = text_color
