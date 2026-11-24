class CBoss:
    """Jefe MOTHER BASE. phase: "turrets" (nucleo cerrado), "core" (nucleo abierto) o "dying"
    bar_entity: relleno de la barra de vida del HUD"""

    def __init__(self, core_hp: int, bar_entity: int, bar_width: int) -> None:
        self.phase = "turrets"
        self.core_hp = core_hp
        self.max_core_hp = core_hp
        self.bar_entity = bar_entity
        self.bar_width = bar_width
        self.launch_timer = 0.0
        self.fan_timer = 0.0
        self.death_timer = 0.0
        self.explosion_timer = 0.0
