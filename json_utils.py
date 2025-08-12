

##################################################################################################################
##                                    FUNCTIONS TO READ JSON FILES FROM AUTOROL 3.0                            ##
##################################################################################################################

import json
import re


def read_json(path: str):

    with open(path, 'r') as file:       #open json in read ('r') mode.
        jsonfile = json.load(file)
    return jsonfile


def get_scenes(jsonfile, formatted=False):

    if formatted:
        format_kivy_all (jsonfile)
    return jsonfile ['escenas']


def format_kivy_all(jsonfile):

    for scene in jsonfile['escenas']:

        for text in scene['textos']:
            if text['texto'][:2] != '<p': #some text does not have new paragraph tag. Must be added
                text['texto'] = '<p>'+ text['texto'] + '</p>'
            text['texto'] = format_kivy (text['texto'])

            for link in text['enlaces']:
                link['texto'] = re.sub(r'<[^>]*>', '', link['texto'])

    return jsonfile


def get_scene(id, scenes):

    for scene in scenes:
        if scene['id'] == id:
            return scene
        

def get_intro(scenes, id_only = False):

    links = get_all_links(scenes)

    for scene in scenes:
        if scene['id'] not in links:
            if id_only:
                return scene['id']
            else:
                return scene


################################ VARIABLES ###############################


def get_variables(scenes):

    variables = dict()

    for scene in scenes:
        for text in scene ['textos']:
            for condition in text['condiciones']:
                variables.update({condition['variable']: 0})

        for text in scene ['textos']:
            for link in text ['enlaces']:
                for condition in link ['condiciones']:
                    variables.update({condition['variable']: 0})

    return variables


def compare_conditions(variables, conditions):

    return all(
        key not in conditions or conditions[key] == variables[key]
        for key in variables
    )


def get_conditions(item):

    item_conditions = dict()
    for condition in item['condiciones']:
        item_conditions.update({condition['variable']: int(condition['valorComparar'])})
    return item_conditions


def get_consequences(item):

    item_consequences = dict()
    for consequence in item['consecuencias']:
        item_consequences.update({consequence['variable']: int(consequence['valor'])})
    return item_consequences


######################################### TEXT ################################################


def get_text(scene):
    
    texts = list()
    for text in scene ['textos']:
        texts.append(text)
    return texts


def format_kivy(text):  # default 0, buttons do not pass index so /n/n are not removed

    #CHECK FOR IMAGE
    if text.find('<img src=') != -1:  # if text has a image tag (text.find returns -1 if not found)
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

    pattern = r'/([^/]+\.(?:png|jpeg|jpg))'     #images as .png or .jpeg are supported
    match = re.search(pattern, text)
        
    if match:
        image_name = match.group(1)
        return '[$image]' + image_name


def align(text):
    
    if text [:9] == '[$center]':
        alignment = 'center'
    else:
        alignment = 'left'
    text = re.sub(r'\[\$center\]', '', text)  # removes any [$center] tag that accidentally is the text
    return [text, alignment]


###################################################### LINKS #########################################


def get_all_links(scenes):

    links = set()
    for scene in scenes:
        for text in scene ['textos']:
            for link in text ['enlaces']:
                links.add(link ['destinoExito'])
    return links


def get_links(text):

    links = list()
        
    for link in text['enlaces']:
        links.append(link)

    return links


def get_links_fates(text):

    links = dict()
    
    for link in text ['enlaces']:
        links.update({link['texto']: link['destinoExito']})

    return links    