class CSceneTimer:

    def __init__(self, duration:float, next_scene:str) -> None:
        self.time = duration
        self.next_scene = next_scene