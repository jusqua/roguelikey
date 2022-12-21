from components.consumable import ConfusionConsumable, FireballDamageConsumable, HealingConsumable, LightningDamageConsumable
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item
from components.ai import HostileEnemy
from components.fighter import Fighter


player = Actor(HostileEnemy, Fighter(30, 5, 2), Level(level_up_base=200), "Player", "@", inventory=Inventory(26))
orc = Actor(HostileEnemy, Fighter(10, 3, 0), Level(xp_given=35), "Orc", "o", (63, 127, 63))
troll = Actor(HostileEnemy, Fighter(16, 4, 1), Level(xp_given=100), "Troll", "T", (0, 127, 0))

health_potion = Item(HealingConsumable(4), "Health Potion", "!", (127, 0, 255))
lightning_scroll = Item(LightningDamageConsumable(20, 5), "Lighting Scroll", "~", (255, 255, 0))
confusion_scroll = Item(ConfusionConsumable(10), "Confusion Scroll", "~", (207, 63, 255))
fireball_scroll = Item(FireballDamageConsumable(3, 12), "Fireball Scroll", "~", (255, 0, 0))

