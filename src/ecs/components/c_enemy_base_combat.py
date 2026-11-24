import pygame

from src.create.enemy_base_composer import (
    DEFAULT_CORE_CENTER,
    DEFAULT_MODULE_CENTERS,
    DEFAULT_LEFT_CONNECTOR_POSITION,
    DEFAULT_LEFT_SUPPORT_POSITION,
    DEFAULT_RIGHT_CONNECTOR_POSITION,
    DEFAULT_RIGHT_SUPPORT_POSITION,
    enemy_base_composer,
)

BASE_SIZE = (99, 80)
_EYE_RECT = pygame.Rect(39, 30, 20, 20)
_NODE_SIZE = 16


class CEnemyBaseCombat:

    def __init__(
        self,
        supports: tuple,
        connectors: tuple,
        eye_frames: list,
        node_frames: list,
        node_centers=DEFAULT_MODULE_CENTERS,
        orientation: str = "horizontal",
    ) -> None:
        self.left_support, self.right_support = supports
        self.left_connector, self.right_connector = connectors
        self.eye_frames = eye_frames
        self.node_frames = node_frames
        self.node_centers = node_centers
        self.node_damage = [0] * 6
        self.node_destroyed = [False] * 6
        self.eye_frame_index = 0
        self.orientation = orientation

    def compose(self) -> pygame.Surface:
        """Compone cada nodo avanzando un estado visual por impacto."""
        nodes = [
            self.node_frames[min(damage, 3)][index]
            for index, damage in enumerate(self.node_damage)
        ]
        surface = enemy_base_composer(
            self.left_support,
            self.right_support,
            self.left_connector,
            self.right_connector,
            self.eye_frames[self.eye_frame_index],
            *nodes,
            module_centers=self.node_centers,
            core_center=DEFAULT_CORE_CENTER,
            left_support_position=DEFAULT_LEFT_SUPPORT_POSITION,
            right_support_position=DEFAULT_RIGHT_SUPPORT_POSITION,
            left_connector_position=DEFAULT_LEFT_CONNECTOR_POSITION,
            right_connector_position=DEFAULT_RIGHT_CONNECTOR_POSITION,
        )
        if self.orientation == "vertical":
            surface = pygame.transform.rotate(surface, 90)
        return surface

    def _local_point(self, point:pygame.Vector2) -> pygame.Vector2:
        """Punto de la base horizontal llevado a la orientacion real"""
        if self.orientation == "vertical":
            return pygame.Vector2(point.y, BASE_SIZE[0] - point.x)
        return pygame.Vector2(point)

    def _local_rect(self, rect:pygame.Rect, base_pos:pygame.Vector2) -> pygame.Rect:
        """Rect de la base horizontal llevado a la orientacion real y al mundo"""
        if self.orientation == "vertical":
            rect = pygame.Rect(rect.y, BASE_SIZE[0] - rect.x - rect.w, rect.h, rect.w)
        return rect.move(round(base_pos.x), round(base_pos.y))

    def get_size(self) -> tuple:
        if self.orientation == "vertical":
            return (BASE_SIZE[1], BASE_SIZE[0])
        return BASE_SIZE

    def get_core_offset(self) -> pygame.Vector2:
        """Centro del nucleo relativo a la posicion de la base"""
        return self._local_point(DEFAULT_CORE_CENTER)

    def get_core_center(self, base_pos:pygame.Vector2) -> pygame.Vector2:
        return base_pos + self.get_core_offset()

    def get_eye_rect(self, base_pos:pygame.Vector2) -> pygame.Rect:
        return self._local_rect(_EYE_RECT, base_pos)

    def get_node_center(self, base_pos:pygame.Vector2, index:int) -> pygame.Vector2:
        return base_pos + self._local_point(self.node_centers[index])

    def get_node_rect(self, base_pos:pygame.Vector2, index:int) -> pygame.Rect:
        center = self.node_centers[index]
        half = _NODE_SIZE // 2
        rect = pygame.Rect(round(center.x - half), round(center.y - half), _NODE_SIZE, _NODE_SIZE)
        return self._local_rect(rect, base_pos)

    def get_axis(self) -> pygame.Vector2:
        """Eje de la base: por donde el nucleo es vulnerable y lanza enemigos"""
        if self.orientation == "vertical":
            return pygame.Vector2(0, 1)
        return pygame.Vector2(1, 0)

    def is_on_axis(self, velocity:pygame.Vector2) -> bool:
        """La velocidad va mayormente en el eje de la base"""
        if self.orientation == "vertical":
            return abs(velocity.y) > abs(velocity.x)
        return abs(velocity.x) > abs(velocity.y)

    def has_been_destroyed(self) -> bool:
        return all(self.node_destroyed)
