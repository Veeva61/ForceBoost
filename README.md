# ForceBoost

Makes **force grab** (pulling items to your hand from a distance) in **BRUTALISTICK VR** much stronger.

## How it works
The game's force grab uses HurricaneVR force-pull settings. ForceBoost finds all of them (pull, push and per-item settings) and multiplies:
- the pull **force** by **x10**;
- the top **speed** items fly to your hand at by **x3**.

Gravity-glove style grabbers get a shorter flight time. Pairs great with GiantPlayer.

## Configuration (`UserData/MelonPreferences.cfg` -> `[ForceBoost]`)
| Setting | Default | Description |
| --- | --- | --- |
| Enabled | true | Master switch |
| ForceMultiplier | 10 | Pull force multiplier |
| SpeedMultiplier | 3 | Top speed multiplier (higher = items fly in like bullets) |
| Verbose | true | Log every changed setting |

---

# ForceBoost (RU)

Притягивание предметов (force grab) становится намного сильнее: сила ×10, скорость полёта к руке ×3. Отталкивание тоже усиливается. Отлично сочетается с GiantPlayer.

## Building

Requires the .NET 6 SDK and BRUTALISTICK VR with MelonLoader 0.7.3 installed through r2modman
(the game must have been started once so MelonLoader generates the Il2Cpp assemblies).

    dotnet build -c Release -p:GameProfile="<path to your r2modman profile>"

The default profile is `%APPDATA%\r2modmanPlus-local\BrutalistickVr\profiles\Default`.
The built dll is copied into the profile's `Mods` folder.
