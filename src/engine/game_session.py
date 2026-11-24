from src.engine.service_locator import ServiceLocator


class GameSession:
    """Datos que sobreviven entre escenas: nivel, puntaje, vidas y record"""

    def __init__(self, game_cfg:dict) -> None:
        self._cfg = game_cfg
        self.use_saved_levels = True
        self.hi_score = ServiceLocator.save_service.load_hi_score(game_cfg["hi_score"])
        self._saved_hi_score = self.hi_score
        self.new_game()

    def new_game(self):
        self.save_record()
        self.record_at_start = self.hi_score
        self.level = 1
        self.god_mode = False
        self.edited_levels = {}
        self.score = 0
        self.lives = self._cfg["lives"]
        self.continues = 0
        self.lives_lost = 0
        self.next_extra_life = self._cfg["extra_life"]["first"]

    def level_override(self):
        """Ronda editada: lo de esta ejecucion o, si no, lo guardado (None si no hay)"""
        if self.level in self.edited_levels:
            return self.edited_levels[self.level]
        if not self.use_saved_levels:
            return None
        return ServiceLocator.save_service.load_levels().get(str(self.level))

    def is_boss_round(self) -> bool:
        """La ronda del jefe es la que indica level.json -> "boss" -> "round" """
        boss = ServiceLocator.configs_service.get("assets/cfg/level.json").get("boss")
        return boss is not None and self.level == boss["round"]

    def continue_game(self):
        """Continuar: recupera todas las vidas y pierde todo el puntaje (mismo lvl)"""
        self.save_record()
        self.score = 0
        self.lives = self._cfg["lives"]
        self.continues += 1
        self.next_extra_life = self._cfg["extra_life"]["first"]

    def is_new_record(self) -> bool:
        """En esta partida se supero el record que habia al empezar
        (cuenta tambien lo logrado antes de continuar)"""
        return self.hi_score > self.record_at_start

    def save_record(self):
        """Escribe el record solo si cambio desde la ultima vez"""
        if self.hi_score > self._saved_hi_score:
            ServiceLocator.save_service.save_hi_score(self.hi_score)
            self._saved_hi_score = self.hi_score

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