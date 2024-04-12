from flask import request
from werkzeug.utils import safe_join

from constants import GACHA_JSON_PATH, POOL_JSON_PATH, POOL_CLASSIC_JSON_PATH, GACHA_TEMP_JSON_PATH, CONFIG_PATH, GACHA_UP_CHAR_JSON_PATH, GACHA_TABLE_URL, POOL_JSON_DIR, CHARACTER_TABLE_URL
from utils import read_json, write_json, decrypt_battle_data
from core.function.update import updateData
import random
import os

from faketime import time


def getTags():
    gacha_table = updateData(GACHA_TABLE_URL)
    all_tags = [
        i["tagId"] for i in gacha_table["gachaTags"]
        if i["tagId"] < 1000
    ]
    tags = random.sample(all_tags, 5)
    return tags


def buildTagCharSet(mode):
    tag_char_set = {}
    tag_char_set["EVERYONE"] = set()
    gacha_table = updateData(GACHA_TABLE_URL)
    for i in gacha_table["gachaTags"]:
        tag_char_set[i["tagName"]] = set()

    if mode == "cn":
        string_mapping = {
            "WARRIOR": "近卫干员",
            "SNIPER": "狙击干员",
            "TANK": "重装干员",
            "MEDIC": "医疗干员",
            "SUPPORT": "辅助干员",
            "CASTER": "术师干员",
            "SPECIAL": "特种干员",
            "PIONEER": "先锋干员",
            "MELEE": "近战位",
            "RANGED": "远程位",
            "TIER_6": "高级资深干员",
            "TIER_5": "资深干员"
        }
    else:
        string_mapping = {
            "WARRIOR": "Guard",
            "SNIPER": "Sniper",
            "TANK": "Defender",
            "MEDIC": "Medic",
            "SUPPORT": "Supporter",
            "CASTER": "Caster",
            "SPECIAL": "Specialist",
            "PIONEER": "Vanguard",
            "MELEE": "Melee",
            "RANGED": "Ranged",
            "TIER_6": "Top Operator",
            "TIER_5": "Senior Operator"
        }

    character_table = updateData(CHARACTER_TABLE_URL)
    for i in character_table:
        if not i.startswith("char_") or i == "char_512_aprot":
            continue
        tag_char_set["EVERYONE"].add(i)
        tag_char_set[string_mapping[character_table[i]["profession"]]].add(i)
        tag_char_set[string_mapping[character_table[i]["position"]]].add(i)
        if character_table[i]["rarity"] == "TIER_6" or character_table[i]["rarity"] == "TIER_5":
            tag_char_set[string_mapping[character_table[i]["rarity"]]].add(i)
        for j in character_table[i]["tagList"]:
            if j in tag_char_set:
                tag_char_set[j].add(i)

    return tag_char_set


def doNormalWish(slot_id, tag_list, mode):
    gacha_table = updateData(GACHA_TABLE_URL)
    int_string_mapping = {}
    string_int_mapping = {}
    for i in gacha_table["gachaTags"]:
        int_string_mapping[i["tagId"]] = i["tagName"]
        string_int_mapping[i["tagName"]] = i["tagId"]

    chosen_tag_list = []
    unchosen_tag_list = []

    string_tag_list = [int_string_mapping[i] for i in tag_list]
    random.shuffle(string_tag_list)

    tag_char_set = buildTagCharSet(mode)
    current_char_set = tag_char_set["EVERYONE"]
    for i in string_tag_list:
        tmp_char_set = current_char_set.intersection(tag_char_set[i])
        if tmp_char_set:
            current_char_set = tmp_char_set
            chosen_tag_list.append(string_int_mapping[i])
        else:
            unchosen_tag_list.append(string_int_mapping[i])
    char_id = random.choice(list(current_char_set))

    gachaTemp = read_json(GACHA_TEMP_JSON_PATH)
    if "normal" not in gachaTemp:
        gachaTemp["normal"] = {}
    gachaTemp["normal"][slot_id] = char_id
    write_json(gachaTemp, GACHA_TEMP_JSON_PATH)

    return chosen_tag_list, unchosen_tag_list


def normalGacha():
    config = read_json(CONFIG_PATH)
    simulateGacha = config["userConfig"]["simulateGacha"]
    request_json = request.json
    start_ts = int(time())
    slot_id = str(request_json["slotId"])
    tag_list = request_json["tagList"]
    if simulateGacha:
        mode = config["server"]["mode"]
        chosen_tag_list,  unchosen_tag_list = doNormalWish(
            slot_id, tag_list, mode
        )
        select_tags = [
            {
                "tagId": i,
                "pick": 1
            } for i in chosen_tag_list
        ]+[
            {
                "tagId": i,
                "pick": 0
            } for i in unchosen_tag_list
        ]
    else:
        select_tags = [
            {
                "tagId": i,
                "pick": 1
            } for i in tag_list
        ]
    data = {
        "playerDataDelta": {
            "modified": {
                "recruit": {
                    "normal": {
                        "slots": {
                            slot_id: {
                                "state": 2,
                                "selectTags": select_tags,
                                "startTs": start_ts,
                                "durationInSec": request_json["duration"],
                                "maxFinishTs": start_ts+request_json["duration"],
                                "realFinishTs": start_ts+request_json["duration"]
                            }
                        }
                    }
                }
            },
            "deleted": {}
        }
    }
    if simulateGacha:
        data["playerDataDelta"]["modified"]["recruit"]["normal"]["slots"][slot_id]["tags"] = getTags()
    return data


def boostNormalGacha():
    request_json = request.json
    real_finish_ts = int(time())
    return {
        "playerDataDelta": {
            "modified": {
                "recruit": {
                    "normal": {
                        "slots": {
                            str(request_json["slotId"]): {
                                "state": 3,
                                "realFinishTs": real_finish_ts
                            }
                        }
                    }
                }
            },
            "deleted": {}
        }
    }


def finishNormalGacha():
    config = read_json(CONFIG_PATH)
    simulateGacha = config["userConfig"]["simulateGacha"]
    request_json = request.json
    slot_id = str(request_json["slotId"])
    if simulateGacha:
        gachaTemp = read_json(GACHA_TEMP_JSON_PATH)
        char_id = gachaTemp["normal"][slot_id]
        is_new = True
    else:
        gacha = read_json(GACHA_JSON_PATH)
        char_id = gacha["normal"]["charId"]
        is_new = gacha["normal"]["isNew"]
    char_inst_id = int(char_id.split('_')[1])
    return {
        "result": 0,
        "charGet": {
            "charInstId": char_inst_id,
            "charId": char_id,
            "isNew": is_new,
            "itemGet": [
                {
                    "type": "HGG_SHD",
                    "id": "4004",
                    "count": 999

                },
                {
                    "type": "LGG_SHD",
                    "id": "4005",
                    "count": 999
                },
                {
                    "type": "MATERIAL",
                    "id": f"p_{char_id}",
                    "count": 999
                }
            ],
            "logInfo": {}
        },
        "playerDataDelta": {
            "modified": {
                "recruit": {
                    "normal": {
                        "slots": {
                            slot_id: {
                                "state": 1,
                                "selectTags": [],
                                "startTs": -1,
                                "durationInSec": -1,
                                "maxFinishTs": -1,
                                "realFinishTs": -1
                            }
                        }
                    }
                }
            },
            "deleted": {}
        }
    }


def syncNormalGacha():
    return {
        "playerDataDelta": {
            "modified": {},
            "deleted": {}
        }
    }


def refreshTags():
    config = read_json(CONFIG_PATH)
    simulateGacha = config["userConfig"]["simulateGacha"]
    request_json = request.json
    slot_id = str(request_json["slotId"])
    data = {
        "playerDataDelta": {
            "modified": {
                "recruit": {
                    "normal": {
                        "slots": {
                        }
                    }
                }
            },
            "deleted": {}
        }
    }
    if simulateGacha:
        data["playerDataDelta"]["modified"]["recruit"]["normal"]["slots"][slot_id] = {
            "tags": getTags()
        }
    return data


def doGetPool(poolId):
    gacha_table = updateData(GACHA_TABLE_URL)
    is_valid = False
    for i in gacha_table["gachaPoolClient"]:
        if i["gachaPoolId"] == poolId:
            is_valid = True
    for i in gacha_table["newbeeGachaPoolClient"]:
        if i["gachaPoolId"] == poolId:
            is_valid = True
    if is_valid:
        pool_file = safe_join(POOL_JSON_DIR, poolId+".json")
        if os.path.isfile(pool_file):
            pool = read_json(pool_file, encoding="utf-8")
            return pool
    if "CLASSIC_" in poolId:
        pool = read_json(POOL_CLASSIC_JSON_PATH, encoding="utf-8")
    else:
        pool = read_json(POOL_JSON_PATH, encoding="utf-8")
    return pool


def doWishes(num, poolId):
    chars = []
    pool = doGetPool(poolId)
    rankChars = {}
    rankProb = {}
    for i in pool["detailInfo"]["availCharInfo"]["perAvailList"]:
        rankChars[i["rarityRank"]] = i["charIdList"]
        rankProb[i["rarityRank"]] = i["totalPercent"]
    if pool["detailInfo"]["weightUpCharInfoList"]:
        for i in pool["detailInfo"]["weightUpCharInfoList"]:
            rankChars[i["rarityRank"]] += [
                i["charId"]
                for j in range(
                    int(i["weight"]/100)-1
                )
            ]
    rankUpChars = {}
    rankUpProb = {}
    if pool["detailInfo"]["upCharInfo"]:
        for i in pool["detailInfo"]["upCharInfo"]["perCharList"]:
            rankUpChars[i["rarityRank"]] = i["charIdList"]
            rankUpProb[i["rarityRank"]] = i["percent"] * i["count"]
    pool_is_single = poolId.startswith("SINGLE_")
    pool_is_linkage = poolId.startswith("LINKAGE_")
    pool_is_boot = poolId.startswith("BOOT_")
    gachaTemp = read_json(GACHA_TEMP_JSON_PATH)
    if poolId not in gachaTemp:
        gachaTemp[poolId] = {
            "numTotal": 0,
            "numWish": 0,
            "numWishUp": 0,
            "first5Star": 0
        }
    numTotal = gachaTemp[poolId]["numTotal"]
    numWish = gachaTemp[poolId]["numWish"]
    numWishUp = gachaTemp[poolId]["numWishUp"]
    first5Star = gachaTemp[poolId]["first5Star"]
    for i in range(num):
        rankUpperLimit = {}
        if numWish < 50:
            rankUpperLimit[5] = rankProb[5]
        else:
            rankUpperLimit[5] = (numWish - 48)*rankProb[5]
        for j in range(4, 1, -1):
            rankUpperLimit[j] = rankUpperLimit[j+1]+rankProb[j]
        if (pool_is_linkage and numWishUp == 119) or (pool_is_boot and numWish == 9 and numTotal == 9):
            rankUpperLimit[5] = 1
        if (not pool_is_boot and first5Star == 9) or (pool_is_boot and first5Star == 19):
            rankUpperLimit[4] = 1
        r = random.random()
        for rank in range(5, 1, -1):
            if r < rankUpperLimit[rank]:
                break
        if first5Star != -1:
            if (not pool_is_boot and rank >= 4) or (pool_is_boot and (rank == 4 or (rank == 5 and numWish < numTotal))):
                first5Star = -1
            else:
                first5Star += 1
        numTotal += 1
        if rank == 5:
            numWish = 0
        else:
            numWish += 1
        if rank in rankUpChars:
            if (pool_is_single and rank == 5 and numWishUp >= 150) or (pool_is_linkage and numWishUp == 119):
                r = 0
            else:
                r = random.random()
            if r < rankUpProb[rank]:
                char_id = random.choice(rankUpChars[rank])
                if numWishUp != -1:
                    if rank == 5:
                        if pool_is_single and numWishUp < 150:
                            numWishUp = 0
                        else:
                            numWishUp = -1
                    else:
                        numWishUp += 1
            else:
                char_id = random.choice(rankChars[rank])
                if numWishUp != -1:
                    numWishUp += 1
        else:
            char_id = random.choice(rankChars[rank])
            if numWishUp != -1:
                numWishUp += 1
        chars.append(
            {
                "charId": char_id,
                "isNew": 1
            }
        )
    gachaTemp[poolId]["numTotal"] = numTotal
    gachaTemp[poolId]["numWish"] = numWish
    gachaTemp[poolId]["numWishUp"] = numWishUp
    gachaTemp[poolId]["first5Star"] = first5Star
    write_json(gachaTemp, GACHA_TEMP_JSON_PATH)
    if pool_is_boot:
        gacha_data = {
            "newbee": {
                "openFlag": int(numTotal < 20),
                "cnt": 20-numTotal
            }
        }
    else:
        gacha_data = {
            "normal": {
                poolId: {
                    "cnt": numTotal,
                    "maxCnt": 10,
                    "rarity": 4,
                    "avail": first5Star != -1
                }
            }
        }
        if pool_is_single:
            gacha_data["single"] = {
                poolId: {
                    "singleEnsureCnt": -1 if numWishUp >= 150 else numWishUp,
                    "singleEnsureUse": numWishUp == -1,
                    "singleEnsureChar": rankUpChars[5][0]
                }
            }
        if pool_is_linkage:
            gacha_table = updateData(GACHA_TABLE_URL)
            for i in gacha_table["gachaPoolClient"]:
                if i["gachaPoolId"] == poolId:
                    gacha_data["linkage"] = {
                        poolId: {
                            i["linkageRuleId"]: {
                                "must6": numWishUp != -1
                            }
                        }
                    }
                    break
    return chars, gacha_data


def advancedGacha():
    request_json = request.json
    poolId = request_json["poolId"]
    config = read_json(CONFIG_PATH)
    simulateGacha = config["userConfig"]["simulateGacha"]
    if simulateGacha:
        chars, gacha_data = doWishes(1, poolId)
    else:
        gacha = read_json(GACHA_JSON_PATH)
        chars = gacha["advanced"]
        gacha_data = {}
    char_id = chars[0]["charId"]
    is_new = chars[0]["isNew"]
    char_inst_id = int(char_id.split('_')[1])
    return {
        "result": 0,
        "charGet": {
            "charInstId": char_inst_id,
            "charId": char_id,
            "isNew": is_new,
            "itemGet": [
                {
                    "type": "HGG_SHD",
                    "id": "4004",
                    "count": 999

                },
                {
                    "type": "LGG_SHD",
                    "id": "4005",
                    "count": 999
                },
                {
                    "type": "MATERIAL",
                    "id": f"p_{char_id}",
                    "count": 999
                }
            ],
            "logInfo": {}
        },
        "playerDataDelta": {
            "modified": {
                "gacha": gacha_data
            },
            "deleted": {}
        }
    }


def tenAdvancedGacha():
    request_json = request.json
    poolId = request_json["poolId"]
    config = read_json(CONFIG_PATH)
    simulateGacha = config["userConfig"]["simulateGacha"]
    if simulateGacha:
        chars, gacha_data = doWishes(10, poolId)
    else:
        gacha = read_json(GACHA_JSON_PATH)
        chars = gacha["advanced"]
        gacha_data = {}
    gachaResultList = []
    j = 0
    for i in range(10):
        char_id = chars[j]["charId"]
        is_new = chars[j]["isNew"]
        char_inst_id = int(char_id.split('_')[1])
        gachaResultList.append(
            {
                "charInstId": char_inst_id,
                "charId": char_id,
                "isNew": is_new,
                "itemGet": [
                    {
                        "type": "HGG_SHD",
                        "id": "4004",
                        "count": 999

                    },
                    {
                        "type": "LGG_SHD",
                        "id": "4005",
                        "count": 999
                    },
                    {
                        "type": "MATERIAL",
                        "id": f"p_{char_id}",
                        "count": 999
                    }
                ],
                "logInfo": {}
            }
        )
        j = (j+1) % len(chars)
    return {
        "result": 0,
        "gachaResultList": gachaResultList,
        "playerDataDelta": {
            "modified": {
                "gacha": gacha_data
            },
            "deleted": {}
        }
    }


def getPoolDetail():
    request_json = request.json
    poolId = request_json["poolId"]
    pool = doGetPool(poolId)
    return pool
