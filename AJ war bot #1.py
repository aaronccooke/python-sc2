import sc2
from sc2.bot_ai import BotAI  # Parent AI Class that you will inherit from
from sc2.data import Difficulty
from sc2.data import Race
from sc2.main import run_game
from sc2.player import Bot
from sc2.player import Computer
from sc2 import maps
from sc2 import units
from sc2.constants import *
import random

class AJsBot(BotAI): # inhereits from BotAI (part of BurnySC2)
    async def on_step(self, iteration): # on_step is a method that is called every step of the game.
        print(f"This is my bot in iteration {iteration}") # prints out the iteration number (ie: the step).
        await self.distribute_workers()

        # INFO
        print(f"INFO_ \
                 Minerals: {self.minerals} \
                  Vespene: {self.vespene} \
        Total Supply Used: {self.supply_used} \
          Total Army Size: {self.supply_army} \
        Total Worker Size: {self.supply_workers} \
               MAX Supply: {self.supply_cap} \
        Total Supply Used: {self.supply_used} \
        Total Supply Left: {self.supply_left} \
        Units_ \
               Total Townhalls: {self.townhalls} \
        Total Structures Count: {self.structures} \
                   Total Units: {self.units} \
            Total Worker Count: {self.workers} \
             Idle Worker Count: {self.idle_worker_count} \
              Total Army Count: {self.army_count} \
              Total Warp Gates: {self.warp_gate_count} \
                   Total Larva: {self.larva} \
           Total Gas Buildings: {self.gas_buildings} \
        OtherInformation_ \
          Current Selected Race: {self.race} \
              Current Player Id: {self.player_id} \
        OtherInformation_ \
          1st Townhall Location: {self.start_location} \
        Main Base Ramp Location: {self.main_base_ramp}")

run_game(
    maps.get("AcropolisLE"),
    [Bot(Race.Terran, AJsBot()),
     Computer(Race.Zerg, Difficulty.Easy)],
    realtime=True
)
