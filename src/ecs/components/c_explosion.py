class CExplosion:

    def __init__(self, frames: list, frame_duration: float) -> None:
        self.frames = frames
        self.frame_duration = frame_duration
        self.elapsed_time = 0.0
        self.frame_index = 0
