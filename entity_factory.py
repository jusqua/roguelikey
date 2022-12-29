from components.consumable import (
    ConfusionConsumable,
    FireballDamageConsumable,
    HealingConsumable,
    LightningDamageConsumable,
)
from components.equippable import (
    Dagger,
    EldenRing,
    Hood,
    JeweledRing,
    LeatherCap,
    RustRing,
    Sword,
    Axe,
    Robe,
    LeatherArmor,
    ChainMail,
    VikingHelmet,
)
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
    HostileEnemy, Fighter(16, 4, 1, 1), Level(xp_given=100), "Troll", "T", (0, 127, 0)
)
goblin = Actor(
    HostileEnemy, Fighter(12, 2, 2, 5), Level(xp_given=40), "Goblin", "g", (20, 127, 20)
)
hobgoblin = Actor(
    HostileEnemy,
    Fighter(20, 5, 1),
    Level(xp_given=100),
    "Hobgoblin",
    "G",
    (20, 150, 20),
)

lesser_health_potion = Item(
    "Lesser Health Potion", "!", (127, 0, 255), consumable=HealingConsumable(2)
)
health_potion = Item(
    "Health Potion", "!", (127, 0, 255), consumable=HealingConsumable(4)
)
greater_health_potion = Item(
    "Greater Health Potion", "!", (127, 0, 255), consumable=HealingConsumable(4)
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

hood = Item("Hood", "^", (218, 165, 32), equippable=Hood())
leather_cap = Item("Leather Cap", "^", (218, 165, 32), equippable=LeatherCap())
viking_helmet = Item("Viking Helmet", "^", (218, 165, 32), equippable=VikingHelmet())

rust_ring = Item("Rust Ring", "°", (30, 144, 255), equippable=RustRing())
jeweled_ring = Item("Jeweled Ring", "°", (30, 144, 255), equippable=JeweledRing())
elden_ring = Item("Elden Ring", "°", (30, 144, 255), equippable=EldenRing())
