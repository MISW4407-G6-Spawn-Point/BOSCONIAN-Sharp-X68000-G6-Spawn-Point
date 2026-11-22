class GameSession:
    """Datos que sobreviven entre escenas: nivel, puntaje, vidas y record"""

    def __init__(self, game_cfg:dict) -> None:
        self._cfg = game_cfg
        self.hi_score = game_cfg["hi_score"]
        self.new_game()

    def new_game(self):
        self.level = 1
        self.score = 0
        self.lives = self._cfg["lives"]
        self.continues = 0
        self.lives_lost = 0
        self.next_extra_life = self._cfg["extra_life"]["first"]

    def continue_game(self):
        """Continuar: recupera todas las vidas y pierde todo el puntaje (mismo lvl)"""
        self.score = 0
        self.lives = self._cfg["lives"]
        self.continues += 1
        self.next_extra_life = self._cfg["extra_life"]["first"]

    def update_score(self, score:int) -> bool:
        """Actualiza puntaje y record y devuelve True si se gano una vida extra"""
        self.score = score
        self.hi_score = max(self.hi_score, score)
        if score < self.next_extra_life:
            return False
        self.lives += 1
        extra = self._cfg["extra_life"]
        if self.next_extra_life < extra["second"]:
            self.next_extra_life = extra["second"]
        else:
            self.next_extra_life += extra["every"]
        return True