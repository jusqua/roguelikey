from components.consumable import HealingConsumable
from components.inventory import Inventory
from entity import Actor, Item
from components.ai import HostileEnemy
from components.fighter import Fighter


player = Actor(HostileEnemy, Fighter(30, 5, 2), "Player", "@", inventory=Inventory(26))
orc = Actor(HostileEnemy, Fighter(10, 3, 0), "Orc", "o", (63, 127, 63))
troll = Actor(HostileEnemy, Fighter(16, 4, 1), "Troll", "T", (0, 127, 0))
health_potion = Item(HealingConsumable(4), "Health Potion", "!", (127, 0, 255))

