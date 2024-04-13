# OpenDoctoratePy

It's a pity that DoctoratePy is no longer maintained. Therefore, this repo aims to continue the support of this project for newer versions of the game.

Python server implementation of a certain anime tower defense game. This repo is for the CN TapTap Version.

Discord: [https://discord.com/invite/SmuB88RR5W](https://discord.com/invite/SmuB88RR5W)

## Currently tested emulator to be working

1. MuMu Player 12 (**recommended**)

2. LDPlayer9 (usable, but **NOT** recommended)

3. BlueStacks 5 (not recommended, but it is the only simple option for the global version of the game)

## How To

### MuMu Player 12

[https://a11.gdl.netease.com/MuMuNG-setup-V3.8.3.2696-overseas-0221213808.exe](https://a11.gdl.netease.com/MuMuNG-setup-V3.8.3.2696-overseas-0221213808.exe)

1. Enable root permission in MuMu Player's settings (adb connection should be enabled by default, therefore no need to enable it manually).
2. Start MuMu Player 12.
3. Run `setup_requirements.bat`, and success can be indicated from `"Press enter to exit..."`.
4. Run `start_local_server.bat`, and the window should stay open if no error occurs.
5. Run `start_frida-server.bat`, and the window should stay open if no error occurs.
6. Run `start_frida-hook.bat`. It should automatically open up the game. The window should stay open if no error occurs.

### LDPlayer9

[https://ldcdn.ldmnq.com/download/package/LDPlayer9.0.exe](https://ldcdn.ldmnq.com/download/package/LDPlayer9.0.exe)

1. Enable root permission and adb connection in LDPlayer9's settings.
2. Start LDPlayer9.
3. Run `setup_requirements.bat`, and success can be indicated from `"Press enter to exit..."`.
4. Run `start_local_server.bat`, and the window should stay open if no error occurs.
5. Run `start_frida-server.bat`, and the window should stay open if no error occurs.
6. Run `start_frida-hook.bat`. It should automatically open up the game. The window should stay open if no error occurs.

### BlueStacks 5

[https://ak-build.bluestacks.com/public/app-player/windows/nxt/5.21.103.1001/03f47a014441168cefa3c6fe6bc5c21e/FullInstaller/x64/BlueStacksFullInstaller_5.21.103.1001_amd64_native.exe](https://ak-build.bluestacks.com/public/app-player/windows/nxt/5.21.103.1001/03f47a014441168cefa3c6fe6bc5c21e/FullInstaller/x64/BlueStacksFullInstaller_5.21.103.1001_amd64_native.exe)

(for global) Please use Android 7 32-bit (x86) emulator (default installation), armeabi-v7a game.

1. Enable adb connection in BlueStacks 5's settings.
2. Open `C:\ProgramData\BlueStacks_nxt\bluestacks.conf` and set `bst.feature.rooting`, `bst.instance.Nougat32.enable_root_access` (and `bst.instance.Nougat64.enable_root_access` if exists) to `"1"` so as to enable root permission.
3. Start BlueStacks 5.
4. Set `"server"` -> `"useSu"` in `config/config.json` to `true`.
5. Run `setup_requirements.bat`, and success can be indicated from `"Press enter to exit..."`.
6. Run `start_local_server.bat`, and the window should stay open if no error occurs.
7. Run `start_frida-server.bat`, and the window should stay open if no error occurs.
8. Run `start_frida-hook.bat`. It should automatically open up the game. The window should stay open if no error occurs. If you are running the global version of the game, please ignore the following output: `"Error: Java API only partially available; please file a bug."`.

## Changing contengency contract season
Change the value of key `selectedCrisis` in `config\config.json` to whatever you want. The avaiable seasons are under `data\crisis`.

## Customizing indivual operators level, potentials, skill ranks and others
Customize each operator indivually by adding new info in `customUnitInfo` key in `config\config.json`. You can find <operator_key_name> from [here](https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/master/zh_CN/gamedata/excel/character_table.json). By default, all characters will have max level, max potentials, max mastery.

- `favorPoint` - Trust points (25570 is 200% Trust) [link to exact point to %](https://gamepress.gg/arknights/core-gameplay/arknights-guide-operator-trust)
- `mainSkillLvl` - Skill Rank (Put mastery at 0 if this is lower than 7)
- `potentialRank` - 0-5
- `evolvePhase` - 0 - E0, 1 - E1, 2 - E2
- `skills` - Mastery level for each skill starting from S1.

### Format
```
"<operator_key_name>": {
    "favorPoint": 25570,
    "mainSkillLvl": 7,
    "potentialRank": 2,
    "level": 50, 
    "evolvePhase": 1,
    "skills": [1, 0]
}
```

## Customizing support unit
Customize the support unit list by changing the unit info in `config/assist.json`. All characters info can be found [here](https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/master/zh_CN/gamedata/excel/character_table.json).

- `charId` - key of the character
- `skillIndex` - Skill Index of the support unit (Index starts from 0).
- `currentEquip` - module of the character

### Format
```
{
    "charId": "char_479_sleach",
    "skillIndex": 2,
    "currentEquip": "uniequip_002_sleach"
}
```

## Preserving In-Game Configurations for Characters, Squads & UI

Set `"userConfig"` -> `"restorePreviousStates"` -> `"squadsAndFavs"` in `config/config.json` to `true` to keep previous configurations for characters and squads.

Set `"userConfig"` -> `"restorePreviousStates"` -> `"ui"` in `config/config.json` to `true` to keep previous configurations for UI.

## Warning!

If you are using your own hook scripts to redirect traffic to ODPY instead of ODPY's frida hook, many features that relies on hooking might be broken, e.g. 3x speed, pause-and-deploy, hp display, forever activity, mods etc.
