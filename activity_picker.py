import json


with open("data/excel/activity_table.json", encoding="utf-8") as f:
    activity_table = json.load(f)
    activity_list = []
    for i in activity_table["basicInfo"]:
        if i.endswith("side") or i == "act1r6sre":
            name = activity_table["basicInfo"][i]["name"]
            startTime = activity_table["basicInfo"][i]["startTime"]
            endTime = activity_table["basicInfo"][i]["endTime"]
            if startTime < 1678161600:
                continue
            activity_list.append((name, startTime, endTime))

for i, activity in enumerate(activity_list):
    name = activity[0]
    print(f"[{i}]", name)

i = int(input("Please Select an Activity: "))

name, startTime, endTime = activity_list[i]

print(name, "Selected")

with open("config/config.json") as f:
    config = json.load(f)

config["userConfig"]["activityMinStartTs"] = startTime
config["userConfig"]["activityMaxStartTs"] = endTime

with open("config/config.json", "w") as f:
    json.dump(config, f, indent=4)
