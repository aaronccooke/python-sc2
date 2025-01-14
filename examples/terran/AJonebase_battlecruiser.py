from pickle import FALSE
from typing import List, Tuple
from typing import Set
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
from sc2.constants import UnitTypeId
import random



class BCRushBot(BotAI):
    reaper_visited_bases = set()
    def random_location_on_map(self) -> Point2:
        """ Returns a random location on the map. """
        map_width = self.game_info.map_size[0]
        map_height = self.game_info.map_size[1]
        target_position = Point2((random.randint(0, map_width), random.randint(0, map_height)))
        return target_position

    
    @staticmethod
    def neighbors4(position, distance=1) -> Set[Point2]:
        p = position
        d = distance
        return {Point2((p.x - d, p.y)), Point2((p.x + d, p.y)), Point2((p.x, p.y - d)), Point2((p.x, p.y + d))}

        # Stolen and modified from position.py
    def neighbors8(self, position, distance=1) -> Set[Point2]:
        p = position
        d = distance
        
        return self.neighbors4(position, distance) | {
            Point2((p.x - d, p.y - d)),
            Point2((p.x - d, p.y + d)),
            Point2((p.x + d, p.y - d)),
            Point2((p.x + d, p.y + d)),
        }

    
    def select_target(self) -> Tuple[Point2, bool]:
        """ Select an enemy target the units should attack. """
        enemy_structures: List[Unit] = self.enemy_structures
        if enemy_structures:
            return enemy_structures.random.position, True

        enemy_units: List[Unit] = self.enemy_units
        if enemy_units:
            return enemy_units.random.position, True

        if self.units and min((u.position.distance_to(self.enemy_start_locations[0]) for u in self.units)) < 5:
            return self.enemy_start_locations[0].position, True

        target_position = self.random_location_on_map()
        return target_position, True

    def factory_points_to_build_addon(self, sp_position: Point2) -> List[Point2]:
        """ Return all points that need to be checked when trying to build an addon. Returns 4 points. """
        addon_offset: Point2 = Point2((2.5, -0.5))
        addon_position: Point2 = sp_position + addon_offset
        addon_points = [
            (addon_position + Point2((x - 0.5, y - 0.5))).rounded for x in range(0, 2) for y in range(0, 2)
        ]
        return addon_points
    # pylint: disable=R0912
    async def on_step(self, iteration):
        ccs: Units = self.townhalls
        # If we no longer have townhalls, attack with all workers
        if not ccs:
            target, target_is_enemy_unit = self.select_target()
            for unit in self.workers | self.units(UnitTypeId.BATTLECRUISER):
                if not unit.is_attacking:
                    unit.attack(target)
            return

        cc: Unit = ccs.random

        # Send all BCs to attack a target.
        bcs: Units = self.units(UnitTypeId.BATTLECRUISER)
        if bcs:
            target, target_is_enemy_unit = self.select_target()
            bc: Unit
            for bc in bcs:
                # Order the BC to attack-move the target
                if target_is_enemy_unit and (bc.is_idle or bc.is_moving):
                    bc.attack(target)
                # Order the BC to move to the target, and once the select_target returns an attack-target, change it to attack-move
                elif bc.is_idle:
                    bc.move(target)
                # Send all Siege Tanks to attack a target.
        tanks: Units = self.units(UnitTypeId.SIEGETANK)
        if tanks:
            target, target_is_enemy_unit = self.select_target()
            tank: Unit
            for tank in tanks:
                # Order the Siege Tank to attack-move the target while in siege mode
                if target_is_enemy_unit and (tank.is_idle or tank.is_moving):
                    tank(AbilityId.SIEGEMODE_SIEGEMODE)
                    tank.attack(target)
                # Order the Siege Tank to move to the target, and once the select_target returns an attack-target, change it to attack-move in siege mode
                elif tank.is_idle:
                    tank.move(target)
        # Build more SCVs until 22
        if self.can_afford(UnitTypeId.SCV) and self.supply_workers < 40 and cc.is_idle:
            cc.train(UnitTypeId.SCV)

        building_bcs = self.units(UnitTypeId.BATTLECRUISER).not_ready
        if not building_bcs:
        # Build more BCs
            if self.structures(UnitTypeId.FUSIONCORE) and self.can_afford(UnitTypeId.BATTLECRUISER):
                for sp in self.structures(UnitTypeId.STARPORT).idle:
                    if sp.has_add_on:
                        if not self.can_afford(UnitTypeId.BATTLECRUISER):
                            break
                        sp.train(UnitTypeId.BATTLECRUISER)
        #     elif self.structures(UnitTypeId.STARPORTTECHLAB) and self.units(UnitTypeId.BANSHEE).amount < 2:
        #         for sp in self.structures(UnitTypeId.STARPORT).idle:
        #             if sp.has_add_on:
        #                 if not self.can_afford(UnitTypeId.BANSHEE):
        #                     break
        #                 sp.train(UnitTypeId.BANSHEE)
        # if self.structures(UnitTypeId.STARPORTTECHLAB) and self.units(UnitTypeId.VIKINGFIGHTER).amount < 1:
        #     for sp in self.structures(UnitTypeId.STARPORT).idle:
        #         if sp.has_add_on:
        #             if not self.can_afford(UnitTypeId.VIKINGFIGHTER):
        #                 break
        #             sp.train(UnitTypeId.VIKINGFIGHTER)
        # if self.structures(UnitTypeId.STARPORTTECHLAB) and self.units(UnitTypeId.MEDIVAC).amount < 1:
        #     for sp in self.structures(UnitTypeId.STARPORT).idle:
        #         if sp.has_add_on:
        #             if not self.can_afford(UnitTypeId.MEDIVAC):
        #                 break
        #             sp.train(UnitTypeId.MEDIVAC)
        # vi: Units = self.units(UnitTypeId.VIKINGFIGHTER)
        # if vi:
        #     target, target_is_enemy_unit = self.select_target()
        #     vi: Unit
        #     for vi in vi:
        #         # Order the BC to attack-move the target
        #         if target_is_enemy_unit and (vi.is_idle or vi.is_moving):
        #             vi.attack(target)
        #         # Order the BC to move to the target, and once the select_target returns an attack-target, change it to attack-move
        #         elif vi.is_idle:
        #             vi.move(target)   
        # ba: Units = self.units(UnitTypeId.BANSHEE) and self.units(UnitTypeId.BANSHEE)
        # if ba:
        #     target, target_is_enemy_unit = self.select_target()
        #     ba: Unit
        #     for ba in ba:
        #         # Order the BC to attack-move the target
        #         if target_is_enemy_unit and (ba.is_idle or ba.is_moving):
        #             ba.attack(target)
        #         # Order the BC to move to the target, and once the select_target returns an attack-target, change it to attack-move
        #         elif ba.is_idle:
        #             ba.move(target)                                                                   

        if self.can_afford(UnitTypeId.REAPER) and self.units(UnitTypeId.REAPER).amount < 1:
            enemy_structures = self.enemy_structures
             # Check if there are no enemy structures
            for sp in self.structures(UnitTypeId.BARRACKS).idle:
                sp.train(UnitTypeId.REAPER)
                sp.move(random.choice(self.enemy_start_locations))
    
            # Build Marines instead
        elif self.can_afford(UnitTypeId.MARINE) and self.units(UnitTypeId.MARINE).amount < 20:
            for rax in self.structures(UnitTypeId.BARRACKS).idle:
                if not self.can_afford(UnitTypeId.MARINE):
                    break
                rax.train(UnitTypeId.MARINE)
        engineeringbay: Units = self.structures(UnitTypeId.ENGINEERINGBAY)
        if not engineeringbay:
            if self.can_afford(UnitTypeId.ENGINEERINGBAY):
                await self.build(UnitTypeId.ENGINEERINGBAY, near=cc.position.towards(self.game_info.map_center, 8)) 
                        # Build missile turrets
        if self.can_afford(UnitTypeId.MISSILETURRET):
            # Find the location near the siege tanks
            tanks: Units = self.units(UnitTypeId.SIEGETANK)
            if tanks:
                tank_position = tanks.closest_to(cc).position
                turret_placement = await self.find_placement(UnitTypeId.MISSILETURRET, near=tank_position, placement_step=1)
                if turret_placement:
                    # Build only one missile turret next to the siege tank
                    if self.already_pending(UnitTypeId.MISSILETURRET) < 2:
                        await self.build(UnitTypeId.MISSILETURRET, near=turret_placement)
                else:
                    # Build missile turret near the command center
                    await self.build(UnitTypeId.MISSILETURRET, near=cc.position.towards(self.game_info.map_center, 8))

        # # Build missile turrets
        # if self.can_afford(UnitTypeId.MISSILETURRET):
        #     # Find the location near the siege tanks
        #     tanks: Units = self.units(UnitTypeId.SIEGETANK)
        #     if tanks:
        #         tank_position = tanks.closest_to(cc).position
        #         turret_placement = await self.find_placement(UnitTypeId.MISSILETURRET, near=tank_position, placement_step=1)
        #         if turret_placement:
        #             await self.build(UnitTypeId.MISSILETURRET, near=turret_placement)
        #             # await self.build(UnitTypeId.SUPPLYDEPOT, near=cc.position.towards(self.game_info.map_center, 8))
        #         else:
        #             await self.build(UnitTypeId.MISSILETURRET, near=cc.position.towards(self.game_info.map_center, 8))

            
        # #Build missile turrets            
        # if self.can_afford(UnitTypeId.MISSILETURRET):
        #     await self.build(UnitTypeId.MISSILETURRET, near=cc.position.towards(self.game_info.map_center, 8))

        # Build more supply depots
        if self.supply_left < 6 and self.supply_used >= 14 and not self.already_pending(UnitTypeId.SUPPLYDEPOT):
            if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                await self.build(UnitTypeId.SUPPLYDEPOT, near=cc.position.towards(self.game_info.map_center, 8))

        # Build barracks if we have none
        if self.tech_requirement_progress(UnitTypeId.BARRACKS) == 1:
            if self.can_afford(UnitTypeId.BARRACKS) and self.structures(UnitTypeId.BARRACKS).amount < 1:
                await self.build(UnitTypeId.BARRACKS, near=cc.position.towards(self.game_info.map_center, 8))

            # Build refineries
            elif self.structures(UnitTypeId.BARRACKS) and self.gas_buildings.amount < 8:
                if self.can_afford(UnitTypeId.REFINERY):
                    vgs: Units = self.vespene_geyser.closer_than(20, cc)
                    for vg in vgs:
                        if self.gas_buildings.filter(lambda unit: unit.distance_to(vg) < 1):
                            break

                        worker: Unit = self.select_build_worker(vg.position)
                        if worker is None:
                            break

                        worker.build_gas(vg)
                        break
            
            # Build factory if we dont have one
            factories: Units = self.structures(UnitTypeId.FACTORY)
            if self.tech_requirement_progress(UnitTypeId.FACTORY) == 1:
                

                if self.can_afford(UnitTypeId.FACTORY) and self.structures(UnitTypeId.FACTORY).amount < 2:
                    await self.build(UnitTypeId.FACTORY, near=cc.position.towards(self.game_info.map_center, 8))
            
            f: Unit
            for f in self.structures(UnitTypeId.FACTORY).ready.idle:
                if not f.has_add_on and self.can_afford(UnitTypeId.FACTORYTECHLAB):
                    addon_points = self.factory_points_to_build_addon(f.position)
                    if all(
                        self.in_map_bounds(addon_point) and self.in_placement_grid(addon_point)
                        and self.in_pathing_grid(addon_point) for addon_point in addon_points
                    ):
                        f.build(UnitTypeId.FACTORYTECHLAB)

            # for f in self.structures(UnitTypeId.FACTORY).ready.idle:
            #     if not f.has_add_on and self.can_afford(UnitTypeId.FACTORYTECHLAB):
            #         addon_points = self.factory_points_to_build_addon(f.position)
            #         if all(
            #             self.in_map_bounds(addon_point) and self.in_placement_grid(addon_point)
            #             and self.in_pathing_grid(addon_point) for addon_point in addon_points
            #         ):
            #             f.build(UnitTypeId.FACTORYTECHLAB)
            #         else:
            #             f(AbilityId.LIFT)

            #             f(AbilityId.LAND)
            #             break
                # Build starport once we can build starports, up to 2
                elif (
                    factories.ready
                    and self.structures.of_type({UnitTypeId.STARPORT, UnitTypeId.STARPORTFLYING}).ready.amount +
                    self.already_pending(UnitTypeId.STARPORT) < 7
                ):
                    if self.can_afford(UnitTypeId.STARPORT):
                        await self.build(
                            UnitTypeId.STARPORT,
                            near=cc.position.towards(self.game_info.map_center, 15).random_on_distance(8),
                        )
        def starport_points_to_build_addon(sp_position: Point2) -> List[Point2]:
            """ Return all points that need to be checked when trying to build an addon. Returns 4 points. """
            addon_offset: Point2 = Point2((2.5, -0.5))
            addon_position: Point2 = sp_position + addon_offset
            addon_points = [
                (addon_position + Point2((x - 0.5, y - 0.5))).rounded for x in range(0, 2) for y in range(0, 2)
            ]
            return addon_points
        # Lower all depots when finished
        for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
            depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)

        # Morph commandcenter to orbitalcommand
        # Check if tech requirement for orbital is complete (e.g. you need a barracks to be able to morph an orbital)
        orbital_tech_requirement: float = self.tech_requirement_progress(UnitTypeId.ORBITALCOMMAND)
        if orbital_tech_requirement == 1:
            # Loop over all idle command centers (CCs that are not building SCVs or morphing to orbital)
            for cc in self.townhalls(UnitTypeId.COMMANDCENTER).idle:
                # Check if we have 150 minerals; this used to be an issue when the API returned 550 (value) of the orbital, but we only wanted the 150 minerals morph cost
                if self.can_afford(UnitTypeId.ORBITALCOMMAND):
                    cc(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND)

        # Expand if we can afford (400 minerals) and have less than 2 bases
        if (
            1 <= self.townhalls.amount < 4 and self.already_pending(UnitTypeId.COMMANDCENTER) == 0
            and self.can_afford(UnitTypeId.COMMANDCENTER)
        ):
            # get_next_expansion returns the position of the next possible expansion location where you can place a command center
            location: Point2 = await self.get_next_expansion()
            if location:
                # Now we "select" (or choose) the nearest worker to that found location
                worker: Unit = self.select_build_worker(location)
                if worker and self.can_afford(UnitTypeId.COMMANDCENTER):
                    # The worker will be commanded to build the command center
                    worker.build(UnitTypeId.COMMANDCENTER, location)
                            # Make scvs until 22, usually you only need 1:1 mineral:gas ratio for reapers, but if you don't lose any then you will need additional depots (mule income should take care of that)
        # Stop scv production when barracks is complete but we still have a command center (priotize morphing to orbital command)
    # pylint: disable=R0916
        if (
            self.can_afford(UnitTypeId.SCV) and self.supply_left > 0 and self.supply_workers < 40 and (
                self.structures(UnitTypeId.FACTORY).ready.amount < 4 and self.townhalls(UnitTypeId.COMMANDCENTER).idle
                or self.townhalls(UnitTypeId.ORBITALCOMMAND).idle
            )
        ):
            for th in self.townhalls.idle:
                th.train(UnitTypeId.SCV)
            # Loop through all idle barracks
        if self.can_afford(UnitTypeId.SIEGETANK) and self.units(UnitTypeId.SIEGETANK):
            for f in self.structures(UnitTypeId.FACTORY).idle:
                self.train(UnitTypeId.SIEGETANK)
                            # Reaper micro
        enemies: Units = self.enemy_units | self.enemy_structures
        enemies_can_attack: Units = enemies.filter(lambda unit: unit.can_attack_ground)
        # if self.can_afford(UnitTypeId.CYCLONE):
        #         for f in self.structures(UnitTypeId.FACTORY).idle:
        #             self.train(UnitTypeId.CYCLONE)
        #                     # Reaper micro
        # cy: Units = self.units(UnitTypeId.CYCLONE)
        # if cy:
        #     target, target_is_enemy_unit = self.select_target()
        #     cy: Unit
        #     for cy in cy:
        #         # Order the BC to attack-move the target
        #         if target_is_enemy_unit and (cy.is_idle or cy.is_moving):
        #             cy.attack(target)
        #         # Order the BC to move to the target, and once the select_target returns an attack-target, change it to attack-move
        #         elif cy.is_idle:
        #             cy.move(target)


        # Add this instance variable outside the loop
        

        for r in self.units(UnitTypeId.REAPER):

            # Move to range 15 of closest unit if reaper is below 20 hp and not regenerating
            enemy_threats_close: Units = enemies_can_attack.filter(
                lambda unit: unit.distance_to(r) < 15
            )  # Threats that can attack the reaper

            if r.health_percentage < 2 / 5 and enemy_threats_close:
                retreat_points: Set[Point2] = self.neighbors8(r.position, distance=2) | self.neighbors8(r.position,
                                                                                                        distance=4)
                # Filter points that are pathable
                retreat_points: Set[Point2] = {x for x in retreat_points if self.in_pathing_grid(x)}
                if retreat_points:
                    closest_enemy: Unit = enemy_threats_close.closest_to(r)
                    retreat_point: Unit = closest_enemy.position.furthest(retreat_points)
                    r.move(retreat_point)
                    continue  # Continue for loop, dont execute any of the following

            # Reaper is ready to attack, shoot nearest ground unit
            enemy_ground_units: Units = enemies.filter(
                lambda unit: unit.distance_to(r) < 5 and not unit.is_flying
            )  # Hardcoded attackrange of 5
            if r.weapon_cooldown == 0 and enemy_ground_units:
                enemy_ground_units: Units = enemy_ground_units.sorted(lambda x: x.distance_to(r))
                closest_enemy: Unit = enemy_ground_units[0]
                r.attack(closest_enemy)
                continue  # Continue for loop, dont execute any of the following

            # Attack is on cooldown, check if grenade is on cooldown, if not then throw it to furthest enemy in range 5
            # pylint: disable=W0212
            reaper_grenade_range: float = (
                self.game_data.abilities[AbilityId.KD8CHARGE_KD8CHARGE.value]._proto.cast_range
            )
            enemy_ground_units_in_grenade_range: Units = enemies_can_attack.filter(
                lambda unit: not unit.is_structure and not unit.is_flying and unit.type_id not in
                {UnitTypeId.LARVA, UnitTypeId.EGG} and unit.distance_to(r) < reaper_grenade_range
            )
            if enemy_ground_units_in_grenade_range and (r.is_attacking or r.is_moving):
                # If AbilityId.KD8CHARGE_KD8CHARGE in abilities, we check that to see if the reaper grenade is off cooldown
                abilities = await self.get_available_abilities(r)
                enemy_ground_units_in_grenade_range = enemy_ground_units_in_grenade_range.sorted(
                    lambda x: x.distance_to(r), reverse=True
                )
                furthest_enemy: Unit = None
                for enemy in enemy_ground_units_in_grenade_range:
                    if await self.can_cast(r, AbilityId.KD8CHARGE_KD8CHARGE, enemy, cached_abilities_of_unit=abilities):
                        furthest_enemy: Unit = enemy
                        break
                if furthest_enemy:
                    r(AbilityId.KD8CHARGE_KD8CHARGE, furthest_enemy)
                    continue  # Continue for loop, don't execute any of the following

            # Move to max unit range if enemy is closer than 4
            enemy_threats_very_close: Units = enemies.filter(
                lambda unit: unit.can_attack_ground and unit.distance_to(r) < 4.5
            )  # Hardcoded attackrange minus 0.5
            # Threats that can attack the reaper
            if r.weapon_cooldown != 0 and enemy_threats_very_close:
                retreat_points: Set[Point2] = self.neighbors8(r.position, distance=2) | self.neighbors8(r.position,
                                                                                                        distance=4)
                # Filter points that are pathable by a reaper
                retreat_points: Set[Point2] = {x for x in retreat_points if self.in_pathing_grid(x)}
                if retreat_points:
                    closest_enemy: Unit = enemy_threats_very_close.closest_to(r)
                    retreat_point: Point2 = max(
                        retreat_points, key=lambda x: x.distance_to(closest_enemy) - x.distance_to(r)
                    )
                    r.move(retreat_point)
                    continue  # Continue for loop, don't execute any of the following
                            # Move to nearest enemy ground unit/building because no enemy unit is closer than 5
            all_enemy_ground_units: Units = self.enemy_units.not_flying
            if all_enemy_ground_units:
                closest_enemy: Unit = all_enemy_ground_units.closest_to(r)
                r.move(closest_enemy)
                continue  # Continue for loop, don't execute any of the following
            enemy_start_locations_set = set(self.enemy_start_locations)
            reaper_visited_bases_set = set(self.reaper_visited_bases)
            # Move to random enemy start location if no enemy buildings have been seen
            if r.is_idle:
                unvisited_bases_set = enemy_start_locations_set.union(reaper_visited_bases_set)
                if unvisited_bases_set:
                    target_base = random.choice(list(unvisited_bases_set))
                    self.reaper_visited_bases.add(target_base)
                    r.move(target_base)
                else:
                    self.reaper_visited_bases = set()

                    # Manage orbital energy and drop mules
        for oc in self.townhalls(UnitTypeId.ORBITALCOMMAND).filter(lambda x: x.energy >= 50):
            mfs: Units = self.mineral_field.closer_than(10, oc)
            if mfs:
                mf: Unit = max(mfs, key=lambda x: x.mineral_contents)
                oc(AbilityId.CALLDOWNMULE_CALLDOWNMULE, mf)

        # Build starport techlab or lift if no room to build techlab
        sp: Unit
        for sp in self.structures(UnitTypeId.STARPORT).ready.idle:
            if not sp.has_add_on and self.can_afford(UnitTypeId.STARPORTTECHLAB):
                addon_points = starport_points_to_build_addon(sp.position)
                if all(
                    self.in_map_bounds(addon_point) and self.in_placement_grid(addon_point)
                    and self.in_pathing_grid(addon_point) for addon_point in addon_points
                ):
                    sp.build(UnitTypeId.STARPORTTECHLAB)
                else:
                    sp(AbilityId.LIFT)

        def starport_land_positions(sp_position: Point2) -> List[Point2]:
            """ Return all points that need to be checked when trying to land at a location where there is enough space to build an addon. Returns 13 points. """
            land_positions = [(sp_position + Point2((x, y))).rounded for x in range(-1, 2) for y in range(-1, 2)]
            return land_positions + starport_points_to_build_addon(sp_position)

        # Find a position to land for a flying starport so that it can build an addon
        for sp in self.structures(UnitTypeId.STARPORTFLYING).idle:
            possible_land_positions_offset = sorted(
                (Point2((x, y)) for x in range(-10, 10) for y in range(-10, 10)),
                key=lambda point: point.x**2 + point.y**2,
            )
            offset_point: Point2 = Point2((-0.5, -0.5))
            possible_land_positions = (sp.position.rounded + offset_point + p for p in possible_land_positions_offset)
            for target_land_position in possible_land_positions:
                land_and_addon_points: List[Point2] = starport_land_positions(target_land_position)
                if all(
                    self.in_map_bounds(land_pos) and self.in_placement_grid(land_pos)
                    and self.in_pathing_grid(land_pos) for land_pos in land_and_addon_points
                ):
                    sp(AbilityId.LAND, target_land_position)
                    break

        # Show where it is flying to and show grid
        unit: Unit
        for sp in self.structures(UnitTypeId.STARPORTFLYING).filter(lambda unit: not unit.is_idle):
            if isinstance(sp.order_target, Point2):
                p: Point3 = Point3((*sp.order_target, self.get_terrain_z_height(sp.order_target)))
                self.client.debug_box2_out(p, color=Point3((255, 0, 0)))

        # Build fusion core
        if self.structures(UnitTypeId.STARPORT).ready:
            if self.can_afford(UnitTypeId.FUSIONCORE) and not self.structures(UnitTypeId.FUSIONCORE):
                await self.build(UnitTypeId.FUSIONCORE, near=cc.position.towards(self.game_info.map_center, 8))

        # Saturate refineries
        for refinery in self.gas_buildings:
            if refinery.assigned_harvesters < refinery.ideal_harvesters:
                worker: Units = self.workers.closer_than(10, refinery)
                if worker:
                    worker.random.gather(refinery)

        # Send workers back to mine if they are idle
        for scv in self.workers.idle:
            scv.gather(self.mineral_field.closest_to(cc))


def main():
    run_game(
        maps.get("(4)DarknessSanctuaryLE"),
        [
            # Human(Race.Protoss),
            Bot(Race.Terran, BCRushBot()),
            #Bot(Race.Terran, BCRushBot()),
            Computer(Race.Terran, Difficulty.VeryHard),
            Computer(Race.Protoss, Difficulty.VeryHard),
            #Computer(Race.Zerg, Difficulty.VeryHard),
            Computer(Race.Zerg, Difficulty.VeryHard),
        ],
        realtime=False,
    )


if __name__ == "__main__":
    main()
