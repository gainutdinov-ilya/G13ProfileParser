import xml.etree.ElementTree as ET

filename = "MyProfile.xml"

namespaces = {
    'Settings': "http://www.logitech.com/Cassandra/2010.7/Profile",
    'Keystroke': "http://www.logitech.com/Cassandra/2010.1/Macros/Keystroke",
}

LinuxKeys = ["KEY_0","KEY_1","KEY_2","KEY_3","KEY_4","KEY_5","KEY_6","KEY_7","KEY_8","KEY_9","KEY_A","KEY_APOSTROPHE","KEY_B","KEY_BACKSLASH","KEY_BACKSPACE","KEY_C","KEY_CAPSLOCK","KEY_COMMA","KEY_D","KEY_DOT","KEY_DOWN","KEY_E","KEY_ENTER","KEY_EQUAL","KEY_ESC","KEY_F","KEY_F1","KEY_F10","KEY_F2","KEY_F3","KEY_F4","KEY_F5","KEY_F6","KEY_F7","KEY_F8","KEY_F9","KEY_G","KEY_GRAVE","KEY_H","KEY_I","KEY_J","KEY_K","KEY_KP0","KEY_KP1","KEY_KP2","KEY_KP3","KEY_KP4","KEY_KP5","KEY_KP6","KEY_KP7","KEY_KP8","KEY_KP9","KEY_KPASTERISK","KEY_KPDOT","KEY_KPMINUS","KEY_KPPLUS","KEY_L","KEY_LEFT","KEY_LEFTALT","KEY_LEFTBRACE","KEY_LEFTCTRL","KEY_LEFTSHIFT","KEY_M","KEY_MINUS","KEY_N","KEY_NUMLOCK","KEY_O","KEY_P","KEY_Q","KEY_R","KEY_RIGHT","KEY_RIGHTBRACE","KEY_RIGHTSHIFT","KEY_S","KEY_SCROLLLOCK","KEY_SEMICOLON","KEY_SLASH","KEY_SPACE","KEY_T","KEY_TAB","KEY_U","KEY_UP","KEY_V","KEY_W","KEY_X","KEY_Y","KEY_Z"]
Macros = list()
Keybinds = list()

class Macro:
    guid: str
    keys: list
    name: str
    keysHash: int

    def __init__(self, Element: ET.Element, name: str, guid: str):
        self.keysHash = 0
        self.keys = list()
        self.guid = guid
        self.name = name
        for key in Element.findall('Keystroke:key', namespaces):
            self.keys.append(key.attrib.get('value'))
        for key in Element.findall('Keystroke:modifier', namespaces):
            self.keys.append(key.attrib.get('value'))
        for key in self.keys:
            for char in key:
                self.keysHash += ord(char)
                self.keysHash *= 4
        
    def toLinux(self) -> str: 
        linuxKeys = []
        for key in self.keys:
            l_key = [unix_key for unix_key in LinuxKeys if unix_key == "KEY_"+str(key)]
            if len(l_key) != 0:
                linuxKeys.append(l_key[0])
            else: 
                match key:
                    case "LALT":
                        linuxKeys.append("KEY_LEFTALT")
                    case "LCTRL":
                        linuxKeys.append("KEY_LEFTCTRL")
                    case "LGUI":
                        linuxKeys.append("KEY_LEFTCTRL")

        return linuxKeys


    def __str__(self):
        return f"Guid: {self.guid}, Keys: {self.keys}, Name: {self.name}, KeysHash: {self.keysHash}"


class Keybind:
    macro: Macro
    gkey: str

    def __init__(self, gkey: str, macro: Macro):
        self.macro = macro
        self.gkey = gkey

    def toLinux(self):
        return self.macro.toLinux()


    def toBind(self):
        linuxKeys = self.toLinux()
        if len(linuxKeys) <= 1:
            return ""
        strBind = f"bind {self.gkey} " 
        for i in range(0, len(linuxKeys)):
            if i == 0:
                strBind += linuxKeys[i]
            else:
                strBind += "+" + linuxKeys[i]
        return strBind


    def __str__(self):
        return f"G-Key: {self.gkey}, Macro: [{self.macro}]"

def main():
    document = ET.parse(filename)
    root = document.getroot()
    profile = root.find('Settings:profile', namespaces)
    if profile == None:
        print("Error: Profile not found")
        return -1
    macros = profile.find("Settings:macros", namespaces)
    if macros == None:
        print("Error: Macros not found")
        return -1
    macros_array = macros.findall("Settings:macro", namespaces)

    for macro in macros_array:
        keystroke = macro.find('Keystroke:keystroke', namespaces)
        if keystroke == None:
            continue
        mac = Macro(keystroke, macro.attrib.get('name'), macro.attrib.get('guid'))
        if len([mc for mc in Macros if mc.keysHash == mac.keysHash]) == 0:
            Macros.append(mac)

    assigment_blocks = profile.findall('Settings:assignments', namespaces)
    for assigment_block in assigment_blocks:
        assigments = assigment_block.findall("Settings:assignment", namespaces)
        for keybind in assigments:
            macros = [mac for mac in Macros if mac.guid == keybind.attrib.get('macroguid')]
            if len(macros) == 0:
                continue
            macro = macros[0]
            keybind_obj = Keybind(keybind.attrib.get('contextid'), macro)
            print(keybind_obj.toBind())
            Keybinds.append(keybind_obj)




if __name__ == "__main__":
    main()