from pymongo import MongoClient

import users
import items
import mobs
import locations
import random

cluster = MongoClient('') #insert special mongo link


def create_user(nickname, user_id):
    finish_game(user_id) #in case something went wrong
    user = users.User
    user["Nickname"] = nickname
    user['UserID'] = user_id
    db = cluster["HW4"]
    collection = db["users"]
    collection.insert_one(user)


def finish_game(user_id):
    db = cluster["HW4"]
    collection = db["users"]
    collection.delete_many({"UserID": user_id})
    collection = db["mobs"]
    collection.delete_many({"UniqueID": user_id})


def check_user(user_id):
    db = cluster["HW4"]
    collection = db["users"]
    return len(list(collection.find({"UserID": user_id})))


def check_trade_possibility(user_id):
    db = cluster["HW4"]
    collection = db["users"]
    return collection.find({"UserID": user_id})[0]['LocationID'] == 1


def travel(user_id):
    print("travel")
    db = cluster["HW4"]
    collection = db["users"]
    user = list(collection.find({"UserID": user_id}))[0]
    if user["LocationID"] == 1:
        return locations.LocationDict[user["LocationID"]]
    collection = db["mobs"]
    print("HERE")
    if len(list(collection.find({"UniqueID": user_id}))) > 0:
        return 0
    else:
        return locations.LocationDict[user["LocationID"]]


def level_up(user_id):
    db = cluster["HW4"]
    collection = db["users"]
    user = list(collection.find({"UserID": user_id}))[0]
    collection.delete_one(user)
    if user["XP"] >= 100:
        user["Level"] += 1
        user["XP"] -= 100
    collection.insert_one(user)


def travel_to(destination, user_id):
    db = cluster["HW4"]
    collection = db["users"]
    user = list(collection.find({"UserID": user_id}))[0]
    collection.delete_one(user)
    user["LocationID"] = locations.LocationNames[str(destination)]
    if user["LocationID"] == 1:
        collection.insert_one(user)
        heal_everything(user_id)
        return 0
    else:
        collection.insert_one(user)
        spawn_mob(user_id)
        return 1


def sell_item(item_name, user_id):
    db = cluster["HW4"]
    collection = db["users"]
    user = list(collection.find({"UserID": user_id}))[0]
    inventory = user["Items"]
    if inventory.get(item_name) is None:
        return 0
    else:
        collection.delete_one(user)
        inventory[item_name] -= 1
        if inventory[item_name] == 0:
            inventory.pop(item_name)
        user["Items"] = inventory
        user["Money"] += items.prices_to_sell[item_name]
        collection.insert_one(user)
        return 1


def buy_item(item_name, user_id):

    if item_name not in list(items.prices_to_buy.keys()):
        return 0
    db = cluster["HW4"]
    collection = db["users"]
    user = list(collection.find({"UserID": user_id}))[0]
    inventory = user["Items"]
    if user['Money'] < items.prices_to_buy[item_name]:
        return 0
    collection.delete_one(user)
    user['Money'] -= items.prices_to_buy[item_name]
    if inventory.get(item_name) is None:
        inventory[item_name] = 1
    else:
        inventory[item_name] += 1
    user["Items"] = inventory
    collection.insert_one(user)
    return 1


def stats(user_id):
    db = cluster["HW4"]
    collection = db["users"]
    user = list(collection.find({"UserID": user_id}))[0]
    info = ""
    for key in user:
        if key in ('_id', 'UserID', 'Items'):
            continue
        if key == "LocationID":
            info = info + "Location" + ": " + str(locations.LocationDict[user[key]]) + '\n'
        else:
            info = info + str(key) + ": " + str(user[key]) + '\n'
    info += "Items: "
    for item in user["Items"]:
        info += str(item) + " - " + str(user["Items"][item]) + " "
    return info


def use_heal_poison(user_id):
    db = cluster["HW4"]
    collection = db["users"]
    user = list(collection.find({"UserID": user_id}))[0]
    inventory = user["Items"]
    if inventory.get("Heal_Poison") is None:
        return 0
    else:
        collection.delete_one(user)
        user["HP"] += 15
        user["HP"] = min(user["HP"], 30)
        inventory["Heal_Poison"] -= 1
        if inventory["Heal_Poison"] == 0:
            inventory.pop("Heal_Poison")
    user["Items"] = inventory
    collection.insert_one(user)
    return 1


def use_mana_poison(user_id):
    db = cluster["HW4"]
    collection = db["users"]
    user = list(collection.find({"UserID": user_id}))[0]
    inventory = user["Items"]
    if inventory.get("Mana_Poison") is None:
        return 0
    else:
        collection.delete_one(user)
        user["Mana"] += 15
        user["Mana"] = min(user["Mana"], 10)
        inventory["Mana_Poison"] -= 1
        if inventory["Mana_Poison"] == 0:
            inventory.pop("Mana_Poison")
    user["Items"] = inventory
    collection.insert_one(user)
    return 1

def spawn_mob(user_id):
    db = cluster["HW4"]
    collection = db["users"]
    user = list(collection.find({"UserID": user_id}))[0]

    #mob_unique_id = mobs.GLOBAL_ENEMY_ID
    #mobs.GLOBAL_ENEMY_ID += 1
    mob_type_id = random.randint(1, user['Level'])

    if mob_type_id == 1:
        new_mob = mobs.Skeleton
    elif mob_type_id == 2:
        new_mob = mobs.RogueArcher
    else:
        new_mob = mobs.GiantSpider

    new_mob["UniqueID"] = user_id
    collection = db["mobs"]
    collection.insert_one(new_mob)


def attack_mob(user_id):
    print("HERE")
    db = cluster['HW4']
    collection = db["users"]
    user = list(collection.find({"UserID": user_id}))[0]
    collection = db["mobs"]
    mob = list(collection.find({"UniqueID": user_id}))[0]
    collection.delete_one(mob)
    attack_physical = 5
    attack_magical = 3
    print("HERE1")
    for item in user["Items"]:
        attack_physical = max(attack_physical, items.physical_attack[item])
        attack_magical = max(attack_magical, items.magic_attack[item])
    print("HERE2")
    attack_physical = max(0, attack_physical - mob["Armour"])
    attack_magical = max(0, attack_magical - mob["Magic Armour"])
    attack = max(attack_physical, attack_magical)
    mob["HP"] = max(0, mob["HP"] - attack)
    if mob["HP"] == 0:
        collection = db["users"]
        collection.delete_one(user)
        user["XP"] += 40
        collection.insert_one(user)
        level_up(user_id)
        return 1
    else:
        collection.insert_one(mob)
        return 0


def mob_attack_you(user_id):
    db = cluster['HW4']
    collection = db["mobs"]
    mob = list(collection.find({"UniqueID": user_id}))[0]
    collection = db["users"]
    user = list(collection.find({"UserID": user_id}))[0]
    collection.delete_one(user)
    armour = 1
    for item in user["Items"]:
        armour = max(armour, items.armour[item])
    mob_attack = max(0, mob["Attack"] - armour)
    user["HP"] = max(0, user["HP"] - mob_attack)
    if user["HP"] > 0:
        collection.insert_one(user)
        return 1
    else:
        return 0


def heal_everything(user_id):
    db = cluster["HW4"]
    collection = db["users"]
    user = list(collection.find({"UserID": user_id}))[0]
    collection.delete_one(user)
    user["Mana"] = 10
    user["HP"] = 30
    collection.insert_one(user)


def enemy_stats(user_id):
    db = cluster['HW4']
    collection = db["mobs"]
    mob = list(collection.find({"UniqueID": user_id}))[0]
    info = ""
    for key in mob:
        if key in ["ModID", "UniqueID", "_id"]:
            continue
        else:
            info = info + str(key) + ": " + str(mob[key]) + '\n'
    return info


