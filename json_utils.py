

##################################################################################################################
##                                    FUNCTIONS TO READ JSON FILES FROM AUTOROL 3.0                            ##
##################################################################################################################

import json
import re


def read_json(path):

    with open(path, "r") as file:       #open json in read ('r') mode.
        jsonfile = json.load(file)
    return jsonfile


def get_scenes(jsonfile, formatted=False):

    if formatted:
        format_kivy_all (jsonfile)
    return jsonfile ["scenes"]


def format_kivy_all(jsonfile):

    for scene in jsonfile["scenes"]:

        for section in scene["sections"]:
            if section["text"][:2] != "<p":  # some text does not have new paragraph tag. Must be added
                section["text"] = "<p>"+ section["text"] + "</p>"
            section["text"] = format_kivy(section["text"])

            for link in section["links"]:
                link["text"] = re.sub(r'<[^>]*>', '', link["text"])

    return jsonfile

def get_intro(scenes, id_only = False):

    links = get_all_destinations(scenes)

    for scene in scenes:
        if scene["id"] not in links:
            if id_only:
                return scene["id"]
            else:
                return scene


################################ VARIABLES ###############################


def get_variables(scenes) -> dict[str,int]:

    variables: dict = {}

    for scene in scenes:
        for section in scene["sections"]:
            for condition in section["conditions"]:
                variables.update({condition["variable"]: 0})

        for section in scene["sections"]:
            for link in section["links"]:
                for condition in link ["conditions"]:
                    variables.update({condition["variable"]: 0})

    return variables


def compare_conditions(variables, conditions) -> bool:
    return all(key not in conditions or conditions[key] == variables[key] for key in variables)


def get_conditions(item) -> dict[str,int]:
    return {condition["variable"]: int(condition["compare_with_value"]) for condition in item["conditions"]}


def get_consequences(item) -> dict[str,int]:
    return {consequence["variable"]: int(consequence["update_to_value"]) for consequence in item["consequences"]}


######################################### TEXT ################################################


def get_sections(scene) -> list[dict]:
    return list(scene["sections"])


def format_kivy(text):  # default 0, buttons do not pass index so /n/n are not removed

    #CHECK FOR IMAGE
    if text.find("<img src=") != -1:  # if text has an image tag (text.find returns -1 if not found)
        clean_text = get_image(text)  # get_image() will delete any text not part of the tag
        return clean_text

    #TEXT ALIGNMENT
    # if not first text, no newline character
    text = re.sub(r'<p\s+style="text-align:\s*center;\s*">', r'[$center]', text, count = 1)

    #NEW LINE CHARACTERS
    # r is for raw string. Treats \ as regular characters and not as escape characters
    text = re.sub(r'<p.*?>', r'\n', text)
    text = re.sub(r'</p.*?>', r'\n', text)

    #REMOVING USELESS TAGS
    for tag in ['span', 'div', 'br']:  # tags to delete
        text = re.sub(r'<'+ tag +'.*?>', '', text)
        text = re.sub(r'</'+ tag +'.*?>', '', text)

    #FORMATTING USEFUL TAGS
    for tag in ['i', 'u', 'b']:  # tags to kivy format
        text = re.sub(r'<'+ tag +'.*?>', r'['+ tag +']', text)
        text = re.sub(r'</'+ tag +'.*?>', r'[/'+ tag +']', text)
        # this monster removes any tag [x] [/x] with no string in between
        text = re.sub(r'\[' + tag + r'\]\[/' + tag + r'\]', '', text)

    # FINAL TOUCHES
    # replaces any occurrence of more than 2 \n in a row by just 2 \n
    text = re.sub(r'\n\s*\n', r'\n\n', text)
    # texts must finish only with one \n. Removes extra \n, if any, at the end of text
    text = re.sub(r'\n\n+$', r'\n', text)
    # removes one \n in case of interlines between italics verses (typically poems or songs)
    text = re.sub(r'\[/i\]\n\n\[i\]', r'[/i]\n[i]', text)
    # removes any \n at the start of text and texts consisting only of \n
    text = re.sub(r'^\n\s*', '', text)
      
    clean_text = re.sub(r'&nbsp;', ' ', text)  # removes residual 'non-breaking space' characters

    return clean_text


def get_image(text):

    pattern = r'/([^/]+\.(?:png|jpeg|jpg))'  # images as .png or .jpeg are supported
    match = re.search(pattern, text)
        
    if match:
        image_name = match.group(1)
        return "[$image]" + image_name


def align(text):
    
    if text [:9] == "[$center]":
        alignment = "center"
    else:
        alignment = "left"
    text = re.sub(r'\[\$center\]', '', text)  # removes any [$center] tag that accidentally is the text
    return [text, alignment]


###################################################### LINKS #########################################


def get_all_destinations(scenes) -> set[int]:
    return {link["destination_scene_id"] for scene in scenes
            for section in scene["sections"] for link in section["links"]}


def get_links(section) -> list[dict]:
    return list(section["links"])