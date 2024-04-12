import json

with open("data/excel/character_table.json", encoding="utf-8") as f:
    character_table = json.load(f)

inst_id_char_id = {}

char_id_char_name = {}

for i in character_table:
    if i.startswith("char_"):
        inst_id = int(i.split('_')[1])
        inst_id_char_id[inst_id] = i
        char_id_char_name[i] = character_table[i]["name"]

with open("data/excel/skill_table.json", encoding="utf-8") as f:
    skill_table = json.load(f)

skill_id_skill_name = {}

for j in skill_table:
    skill_id_skill_name[j] = skill_table[j]["levels"][0]["name"]

skill_id_skill_name[None] = None

with open("data/user/battleReplays.json", encoding="utf-8") as f:
    battle_replay = json.load(f)

currentCharConfig = battle_replay["currentCharConfig"]

num_level = 0

char_taken_cnt = {}
char_skill_taken_cnt = {}

char_used_cnt = {}
char_skill_used_cnt = {}

char_deploy_cnt = {}
skill_cast_cnt = {}

if currentCharConfig in battle_replay["saved"]:
    for i in battle_replay["saved"][currentCharConfig]:
        char_skill_taken = {}
        for j in battle_replay["saved"][currentCharConfig][i]["journal"]["squad"]:
            char_skill_taken[inst_id_char_id[j["charInstId"]]] = j["skillId"]
        for j in char_skill_taken:
            if j not in char_taken_cnt:
                char_taken_cnt[j] = 0
            char_taken_cnt[j] += 1
            if j not in char_skill_taken_cnt:
                char_skill_taken_cnt[j] = {}
            if char_skill_taken[j] not in char_skill_taken_cnt[j]:
                char_skill_taken_cnt[j][char_skill_taken[j]] = 0
            char_skill_taken_cnt[j][char_skill_taken[j]] += 1
        char_used = set()
        for j in battle_replay["saved"][currentCharConfig][i]["journal"]["logs"]:
            if j["signiture"]["charId"] in char_skill_taken:
                char_used.add(j["signiture"]["charId"])
                if j["op"] == 0:
                    if j["signiture"]["charId"] not in char_deploy_cnt:
                        char_deploy_cnt[j["signiture"]["charId"]] = 0
                    char_deploy_cnt[j["signiture"]["charId"]] += 1
                elif j["op"] == 2:
                    if char_skill_taken[j["signiture"]["charId"]] not in skill_cast_cnt:
                        skill_cast_cnt[char_skill_taken[j["signiture"]["charId"]]] = 0
                    skill_cast_cnt[
                        char_skill_taken[j["signiture"]["charId"]]
                    ] += 1
        for j in char_used:
            if j not in char_used_cnt:
                char_used_cnt[j] = 0
            char_used_cnt[j] += 1
            if j not in char_skill_used_cnt:
                char_skill_used_cnt[j] = {}
            if char_skill_taken[j] not in char_skill_used_cnt[j]:
                char_skill_used_cnt[j][char_skill_taken[j]] = 0
            char_skill_used_cnt[j][char_skill_taken[j]] += 1
        num_level += 1

print("Number of Saved Levels:", num_level)
print()

print("Character Taken Count:")
for i in char_taken_cnt:
    print(
        char_id_char_name[i],
        f"{char_taken_cnt[i]}/{num_level} = {100*char_taken_cnt[i]/num_level:.2f}%"
    )
print()

print("Character Skill Taken Count:")
for i in char_skill_taken_cnt:
    for j in char_skill_taken_cnt[i]:
        print(
            char_id_char_name[i],
            skill_id_skill_name[j],
            f"{char_skill_taken_cnt[i][j]}/{char_taken_cnt[i]} = {100*char_skill_taken_cnt[i][j]/char_taken_cnt[i]:.2f}%"
        )
print()

print("Character Used Count:")
for i in char_used_cnt:
    print(
        char_id_char_name[i],
        f"{char_used_cnt[i]}/{num_level} = {100*char_used_cnt[i]/num_level:.2f}%"
    )
print()

print("Character Skill Used Count:")
for i in char_skill_used_cnt:
    for j in char_skill_used_cnt[i]:
        print(
            char_id_char_name[i],
            skill_id_skill_name[j],
            f"{char_skill_used_cnt[i][j]}/{char_used_cnt[i]} = {100*char_skill_used_cnt[i][j]/char_used_cnt[i]:.2f}%"
        )
print()

print("Character Deploy Count:")
for i in char_deploy_cnt:
    print(
        char_id_char_name[i],
        char_deploy_cnt[i]
    )
print()

print("Skill Cast Count:")
for i in skill_cast_cnt:
    print(
        skill_id_skill_name[i],
        skill_cast_cnt[i]
    )
print()
