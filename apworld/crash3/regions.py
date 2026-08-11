from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Entrance, Region

from .locations import levelIdToName, levelNameToId

if TYPE_CHECKING:
    from .world import Crash3World

# A region is a container for locations ("checks"), which connects to other regions via "Entrance" objects.
# Many games will model their Regions after physical in-game places, but you can also have more abstract regions.
# For a location to be in logic, its containing region must be reachable.
# The Entrances connecting regions can have rules - more on that in rules.py.
# This makes regions especially useful for traversal logic ("Can the player reach this part of the map?")

# Every location must be inside a region, and you must have at least one region.
# This is why we create regions first, and then later we create the locations (in locations.py).

crystal_counts = []

def create_and_connect_regions(world: Crash3World) -> None:
    create_all_regions(world)
    connect_regions(world)


def create_all_regions(world: Crash3World) -> None:
    # Creating a region is as simple as calling the constructor of the Region class.
    # overworld = Region("Overworld", world.player, world.multiworld)
    # top_left_room = Region("Top Left Room", world.player, world.multiworld)
    # bottom_right_room = Region("Bottom Right Room", world.player, world.multiworld)
    # right_room = Region("Right Room", world.player, world.multiworld)
    # final_boss_room = Region("Final Boss Room", world.player, world.multiworld)

    regions = []
    for i in range(6): # Warp room 6 is the hidden warp room
        regions.append(Region("Warp Room "+str(i+1), world.player, world.multiworld))


    for name in levelNameToId:
        regions.append(Region(name, world.player, world.multiworld))

    # Let's put all these regions in a list.
    # regions = [overworld, top_left_room, bottom_right_room, right_room, final_boss_room]

    # Some regions may only exist if the player enables certain options.
    # In our case, the Hammer locks the top middle chest in its own room if the hammer option is enabled.
    # if world.options.hammer:
    #     top_middle_room = Region("Top Middle Room", world.player, world.multiworld)
    #     regions.append(top_middle_room)

    # We now need to add these regions to multiworld.regions so that AP knows about their existence.
    world.multiworld.regions += regions


def connect_regions(world: Crash3World) -> None:
    # We have regions now, but still need to connect them to each other.
    # But wait, we no longer have access to the region variables we created in create_all_regions()!
    # Luckily, once you've submitted your regions to multiworld.regions,
    # you can get them at any time using world.get_region(...).
    # overworld = world.get_region("Overworld")
    # top_left_room = world.get_region("Top Left Room")
    # bottom_right_room = world.get_region("Bottom Right Room")
    # right_room = world.get_region("Right Room")
    # final_boss_room = world.get_region("Final Boss Room")

    # Okay, now we can get connecting. For this, we need to create Entrances.
    # Entrances are inherently one-way, but crucially, AP assumes you can always return to the origin region.
    # One way to create an Entrance is by calling the Entrance constructor.
    # overworld_to_bottom_right_room = Entrance(world.player, "Overworld to Bottom Right Room", parent=overworld)
    # overworld.exits.append(overworld_to_bottom_right_room)

    # Connect every warp room to the next warp room, except 5 doesn't connect to 6 (secret warp room)
    # Warp-Räume nacheinander verbinden (Warp Room 1 bis 5)
    for i in range(1, 5):
        world.get_region("Warp Room " + str(i)).connect(
            world.get_region("Warp Room " + str(i+1)),
            "Warp Room " + str(i) + " to Warp Room " + str(i+1))
    
    # Jeden Warp-Raum mit seinen 5 Leveln und dem Boss verbinden
    for i in range(6):
        warp_room = world.get_region("Warp Room " + str(i+1))
        
        # Die 5 regulären Level des Warp-Raums durchgehen
        for j in range(5):
            # Für Crash 3 brauchen wir kein Bit-Anding (& 0x3F oder & 0x100), 
            # da jede Level-ID direkt aus deiner Liste kommt.
            level_id = world.warp_room[i * 5 + j]
            level_name = levelIdToName[level_id]
            level = world.get_region(level_name)
            
            warp_room.connect(level, "Warp Room " + str(i+1) + " to " + level_name)
            
        # Und den Boss hinzufügen (Warp-Raum 6 hat keinen Boss)
        boss_names = ["Tiny Tiger", "Dingodile", "N. Tropy", "N. Gin", "Dr. Neo Cortex"]
        if i < 5:
            level_name = boss_names[i]
            level = world.get_region(level_name)
            warp_room.connect(level, "Warp Room " + str(i+1) + " to " + level_name)
    


    # Connect crystal count regions in a chain

    # You can then connect the Entrance to the target region.
    # overworld_to_bottom_right_room.connect(bottom_right_room)

    # An even easier way is to use the region.connect helper.
    # overworld.connect(right_room, "Overworld to Right Room")
    # right_room.connect(final_boss_room, "Right Room to Final Boss Room")

    # The region.connect helper even allows adding a rule immediately.
    # We'll talk more about rule creation in the set_all_rules() function in rules.py.
    # overworld.connect(top_left_room, "Overworld to Top Left Room", lambda state: state.has("Key", world.player))

    # Some Entrances may only exist if the player enables certain options.
    # In our case, the Hammer locks the top middle chest in its own room if the hammer option is enabled.
    # In this case, we previously created an extra "Top Middle Room" region that we now need to connect to Overworld.
    # if world.options.hammer:
    #     top_middle_room = world.get_region("Top Middle Room")
    #     overworld.connect(top_middle_room, "Overworld to Top Middle Room")