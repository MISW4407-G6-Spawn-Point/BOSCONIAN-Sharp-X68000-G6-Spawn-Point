class CSpriteAnimation:

    def __init__(self, frames: list, frame_duration: float = 1.0) -> None:
        self.frames = frames
        self.frame_duration = frame_duration
        self.elapsed_time = 0.0
        self.frame_index = 0
