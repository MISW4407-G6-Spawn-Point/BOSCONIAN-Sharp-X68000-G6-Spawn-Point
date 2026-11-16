class CEnemyBaseEye:
    def __init__(
        self,
        base_surface,
        eye_frames,
        interval: float = 0.25,
        open_interval_bonus: float = 3.75,
    ) -> None:
        self.base_surface = base_surface
        self.eye_frames = eye_frames
        self.interval = interval
        self.elapsed_time = 0.0
        self.frame_order = (0, 1, 2, 3, 2, 1)
        self.frame_position = 0
        self.open_interval_bonus = open_interval_bonus
