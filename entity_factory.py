from components.consumable import (
    ConfusionConsumable,
    FireballDamageConsumable,
    HealingConsumable,
    LightningDamageConsumable,
)
from components.equippable import Dagger, Sword, Axe, Robe, LeatherArmor, ChainMail
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item
from components.ai import HostileEnemy
from components.fighter import Fighter


player = Actor(
    HostileEnemy,
    Fighter(30, 5, 2, 100),
    Level(level_up_base=200),
    "Player",
    "@",
    inventory=Inventory(26),
)
orc = Actor(
    HostileEnemy, Fighter(10, 3, 0), Level(xp_given=35), "Orc", "o", (63, 127, 63)
)
troll = Actor(
    HostileEnemy, Fighter(16, 4, 1), Level(xp_given=100), "Troll", "T", (0, 127, 0)
)

health_potion = Item(
    "Health Potion", "!", (127, 0, 255), consumable=HealingConsumable(4)
)
lightning_scroll = Item(
    "Lighting Scroll", "~", (255, 255, 0), consumable=LightningDamageConsumable(20, 5)
)
confusion_scroll = Item(
    "Confusion Scroll", "~", (207, 63, 255), consumable=ConfusionConsumable(10)
)
fireball_scroll = Item(
    "Fireball Scroll", "~", (255, 0, 0), consumable=FireballDamageConsumable(3, 12)
)

dagger = Item("Dagger", "/", (0, 191, 255), equippable=Dagger())
sword = Item("Sword", "/", (0, 191, 255), equippable=Sword())
axe = Item("Axe", "/", (0, 191, 255), equippable=Axe())

robe = Item("Robe", "[", (139, 69, 19), equippable=Robe())
leather_armor = Item("Leather Armor", "[", (139, 69, 19), equippable=LeatherArmor())
chain_mail = Item("Chain Mail", "[", (139, 69, 19), equippable=ChainMail())
