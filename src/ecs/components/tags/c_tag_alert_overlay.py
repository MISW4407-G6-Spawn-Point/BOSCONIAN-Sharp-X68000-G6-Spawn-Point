class CTagAlertOverlay:
    """Cartel que tapa CONDITION mientras hay un evento (FORMATION ATTACK!, SPY SHIP)"""

    def __init__(self, kind:str) -> None:
        self.kind = kind