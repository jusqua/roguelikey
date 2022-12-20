from __future__ import annotations
from typing import TYPE_CHECKING
from random import choice
from action import Action, MovementAction, MeleeAction, WaitAction, BumpAction
import numpy as np
import tcod
if TYPE_CHECKING:
    from entity import Actor


class BaseAI(Action):
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


class ConfusedEnemy(BaseAI):
    """
    A confused enemy will stumble around aimlessly for given amount of turns, then revert to previous ai.
    It will attack if an actor occupies a tile it is randomly moving into, it will attack.
    """
    def __init__(self, entity: Actor, previous_ai: BaseAI | None, turns_remaining: int) -> None:
        super().__init__(entity)
        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform(self) -> None:
        if self.turns_remaining <= 0:
            self.engine.message_log.add_message(f"The {self.entity.name} is no longer confused.")
            self.entity.ai = self.previous_ai
            return None

        random_direction = choice([(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)])
        self.turns_remaining -= 1
        return BumpAction(self.entity, *random_direction).perform()

