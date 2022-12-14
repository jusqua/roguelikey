from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
import tcod
from action import Action, MovementAction, MeleeAction, WaitAction
from components.base_component import BaseComponent
if TYPE_CHECKING:
    from entity import Actor


class BaseAI(Action, BaseComponent):
    entity: Actor
    def get_path_to(self, destination: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Compute path to the target position
        If no valid path, return empty list
        """
        cost = np.array(self.entity.game_map.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.game_map.entities:
            if entity.blocks_movement and cost[entity.position]:
                cost[entity.position] += 10

        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)
        pathfinder.add_root(self.entity.position)

        path = pathfinder.path_to(destination)[1:].tolist()
        return [(index[0], index[1]) for index in path]


class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor) -> None:
        super().__init__(entity)
        self.path: list[tuple[int, int]] = []

    def perform(self) -> None:
        target = self.engine.player

        if self.engine.game_map.visible[self.entity.position]:
            dx = target.x - self.entity.x
            dy = target.y - self.entity.y
            if max(abs(dx), abs(dy)) <= 1:
                return MeleeAction(self.entity, dx, dy).perform()
            self.path = self.get_path_to(target.position)

        if self.path:
            x, y = self.path.pop(0)
            dx = x - self.entity.x
            dy = y - self.entity.y
            return MovementAction(self.entity, dx, dy).perform()

        return WaitAction(self.entity).perform()

