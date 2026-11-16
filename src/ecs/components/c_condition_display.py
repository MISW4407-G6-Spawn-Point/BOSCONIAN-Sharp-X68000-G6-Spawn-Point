class CConditionDisplay:
    def __init__(
        self,
        bar_entity: int,
        text_entity: int,
        yellow_time: float,
        red_time: float,
        font_path: str,
        text_size: int,
        text_color,
        text_position,
    ) -> None:
        self.bar_entity = bar_entity
        self.text_entity = text_entity
        self.yellow_time = yellow_time
        self.red_time = red_time
        self.font_path = font_path
        self.text_size = text_size
        self.text_color = text_color
        self.text_position = text_position
        self.elapsed_time = 0.0
        self.phase = "GREEN"
