#!/usr/bin/env python3

import os
import sys

battery = None
energyFull = 0
energyNow = 0
hasBattery = True

def is_on_ac():
    return False
def get_battery_percentage():
    return 100

# Based on http://stackoverflow.com/questions/6153860/in-python-how-can-i-detect-whether-the-computer-is-on-battery-power
if sys.platform.startswith("win"):
    # Get power status of the system using ctypes to call GetSystemPowerStatus

    import ctypes
    from ctypes import wintypes

    class SYSTEM_POWER_STATUS(ctypes.Structure):
        _fields_ = [
            ('ACLineStatus', wintypes.BYTE),
            ('BatteryFlag', wintypes.BYTE),
            ('BatteryLifePercent', wintypes.BYTE),
            ('Reserved1', wintypes.BYTE),
            ('BatteryLifeTime', wintypes.DWORD),
            ('BatteryFullLifeTime', wintypes.DWORD),
        ]

    SYSTEM_POWER_STATUS_P = ctypes.POINTER(SYSTEM_POWER_STATUS)

    GetSystemPowerStatus = ctypes.windll.kernel32.GetSystemPowerStatus
    GetSystemPowerStatus.argtypes = [SYSTEM_POWER_STATUS_P]
    GetSystemPowerStatus.restype = wintypes.BOOL

    status = SYSTEM_POWER_STATUS()
    if not GetSystemPowerStatus(ctypes.pointer(status)):
        raise ctypes.WinError()
    
    if status.BatteryFlag > -128:
        battery = True
    
    def is_on_ac():
        SYSTEM_POWER_STATUS_P = ctypes.POINTER(SYSTEM_POWER_STATUS)

        GetSystemPowerStatus = ctypes.windll.kernel32.GetSystemPowerStatus
        GetSystemPowerStatus.argtypes = [SYSTEM_POWER_STATUS_P]
        GetSystemPowerStatus.restype = wintypes.BOOL

        status = SYSTEM_POWER_STATUS()
        if not GetSystemPowerStatus(ctypes.pointer(status)):
            raise ctypes.WinError()
        acline = bool(status.ACLineStatus)
        del SYSTEM_POWER_STATUS_P
        del status
        return acline
    
    def get_battery_percentage():
        SYSTEM_POWER_STATUS_P = ctypes.POINTER(SYSTEM_POWER_STATUS)

        GetSystemPowerStatus = ctypes.windll.kernel32.GetSystemPowerStatus
        GetSystemPowerStatus.argtypes = [SYSTEM_POWER_STATUS_P]
        GetSystemPowerStatus.restype = wintypes.BOOL

        status = SYSTEM_POWER_STATUS()
        if not GetSystemPowerStatus(ctypes.pointer(status)):
            raise ctypes.WinError()
        percent = status.BatteryLifePercent
        del SYSTEM_POWER_STATUS_P
        del status
        return percent
else:
    power_supplies = "/sys/class/power_supply/"
    ac_status = os.path.join(power_supplies, "ACAD")
    try:
        psups = os.listdir(power_supplies)
    except:
        hasBattery = False
    else:
        for fname in psups:
            if fname.lower().startswith("bat"):
                battery = os.path.join(power_supplies, fname)
                try:
                    f = open(os.path.join(battery, "energy_full"))
                    energyFull = int(f.read())
                    f.close()
                except:
                    pass
                break
            if not battery:
                hasBattery = False

    def get_battery_percentage():
        if os.path.isdir(battery):
            try:
                f = open(os.path.join(battery, "energy_now"))
                energyNow = int(f.read())
                f.close()
            except:
                pass
            else:
                percentage = round(energyNow/energyFull*100, 1)
        return percentage

    def is_on_ac():
        try: f = open(os.path.join(ac_status, "online"))
        except: return 1
        else:
            try: online = int(f.read())
            except: pass
            f.close()
            return bool(online)