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


class CEnemyBaseCombat:

    def __init__(
        self,
        supports: tuple,
        connectors: tuple,
        eye_frames: list,
        node_frames: list,
        node_centers=DEFAULT_MODULE_CENTERS,
    ) -> None:
        self.left_support, self.right_support = supports
        self.left_connector, self.right_connector = connectors
        self.eye_frames = eye_frames
        self.node_frames = node_frames
        self.node_centers = node_centers
        self.node_damage = [0] * 6
        self.node_destroyed = [False] * 6
        self.eye_frame_index = 0

    def compose(self) -> pygame.Surface:
        """Compone cada nodo avanzando un estado visual por impacto."""
        nodes = [
            self.node_frames[min(damage, 3)][index]
            for index, damage in enumerate(self.node_damage)
        ]
        return enemy_base_composer(
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

    def has_been_destroyed(self) -> bool:
        return all(self.node_destroyed)
