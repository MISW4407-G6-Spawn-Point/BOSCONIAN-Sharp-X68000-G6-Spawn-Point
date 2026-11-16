class CLevelObject:

    def __init__(
        self,
        object_type: str,
        score: int,
        node_score: int = 0,
    ) -> None:
        self.object_type = object_type
        self.score = score
        self.node_score = node_score
