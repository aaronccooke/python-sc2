from typing import List, Tuple, Set
from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import run_game
from sc2.player import Bot, Computer, Human
from sc2.position import Point2, Point3
from sc2.unit import Unit
from sc2.units import Units
import random

class BCRushBot(BotAI):
    reaper_visited_bases = set()

    def random_location_on_map(self) -> Point2:
        """ Returns a random location on the map. """
        return random.choice(self.game_info.map_ramps)

    # ... Rest of the code remains the same ...

    def tactical_behavior(self, unit: Unit, target: Point2, target_is_enemy_unit: bool):
        if target_is_enemy_unit and (unit.is_idle or unit.is_moving):
            unit.attack(target)
        elif unit.is_idle:
            unit.move(target)

    async def on_step(self, iteration):
        # ... Rest of the code remains the same ...

        # Send all BCs to attack a target.
        bcs: Units = self.units(UnitTypeId.BATTLECRUISER)
        if bcs:
            target, target_is_enemy_unit = self.select_target()
            for bc in bcs:
                self.tactical_behavior(bc, target, target_is_enemy_unit)

        # ... Rest of the code remains the same ...

        # Send all Siege Tanks to attack a target.
        tanks: Units = self.units(UnitTypeId.SIEGETANK)
        if tanks:
            target, target_is_enemy_unit = self.select_target()
            for tank in tanks:
                # Order the Siege Tank to attack-move the target while in siege mode
                if target_is_enemy_unit and (tank.is_idle or tank.is_moving):
                    tank(AbilityId.SIEGEMODE_SIEGEMODE)
                    self.tactical_behavior(tank, target, target_is_enemy_unit)
                # Order the Siege Tank to move to the target, and once the select_target returns an attack-target, change it to attack-move in siege mode
                elif tank.is_idle:
                    self.tactical_behavior(tank, target, target_is_enemy_unit)

        # ... Rest of the code remains the same ...

def main():
    run_game(
        maps.get("(4)DarknessSanctuaryLE"),
        [
            # Human(Race.Protoss),
            Bot(Race.Terran, BCRushBot()),
            Computer(Race.Terran, Difficulty.VeryHard),
            Computer(Race.Protoss, Difficulty.VeryHard),
            Computer(Race.Zerg, Difficulty.VeryHard),
            Computer(Race.Zerg, Difficulty.VeryHard),
        ],
        realtime=False,
    )

if __name__ == "__main__":
    main()
