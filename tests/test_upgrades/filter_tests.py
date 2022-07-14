"""
The following dictionary contains expected upgrade slots organized
gy faction -> ship -> pilot
This can be used to add to test cases for filtering
"""
FILTER_TESTS = {
    "galactic empire": {
        "lambda-class t-4a shuttle": {
            "omicron group pilot": [
                # SENSOR SLOT
                "fire-control system",
                "passive sensors",
                "collision detector",
                "trajectory simulator",
                "advanced sensors",
                # 2x CREW SLOTS
                "isb slicer",
                "grand inquisitor",
                "novice technician",
                "freelance slicer",
                "seasoned navigator",
                "ciena ree",
                "director krennic",
                "informant",
                "agent kallus",
                "captain hark",
                "gnk ^gonk^ droid",
                "hondo ohnaka",
                "death troopers",
                "gar saxon (crew)",
                "protectorate gleb",
                "the child",
                "minister tua",
                "moff jerjerrod",
                "perceptive copilot",
                "seventh sister",
                "emperor palpatine",
                "imperial super commandos",
                "darth vader",
                "admiral sloane",
                # this one is only if vader is in the squad already
                # "0-0-0",
                # this one is only if the pilot has the target lock action
                # "grand moff tarkin",
                # this one is only if gar saxon is in the squad
                # "tristan wren",
                # this one is only if the pilot has a red coordinate action
                # "tactical officer",
                # CANNON SLOT
                "jamming beam",
                "autoblasters",
                "heavy laser cannon",
                "tractor beam",
                "ion cannon",
                # MODIFICATION SLOT
                "delayed fuses",
                "munitions failsafe",
                "electronic baffle",
                "tactical scrambler",
                "hull upgrade",
                "targeting computer",
                "ablative plating",
                "shield upgrade",
                "stealth device",
                "static discharge vanes",
                # TITLE SLOT
                "st-321",
            ]
        }
    }
}
