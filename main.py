from os import path
import sys
from typing import Optional

from kivy.app import App    # type: ignore
from kivy.uix.boxlayout import BoxLayout    # type: ignore
from kivy.uix.scrollview import ScrollView  # type: ignore
from kivy.uix.label import Label    # type: ignore
from kivy.uix.button import Button  # type: ignore
from kivy.core.text import LabelBase    # type: ignore
from kivy.uix.image import Image    # type: ignore
from kivy.uix.screenmanager import ScreenManager, Screen

import json_utils    # type: ignore

# this is needed to set the correct path to resources when compiling with Pyinstaller
def get_resource_path(relative_path):

    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = path.abspath(".")
    return path.join(base_path, relative_path)

LabelBase.register(name = 'Vollkorn',
                   fn_regular= get_resource_path('fonts/Vollkorn-Regular.ttf'),
                   fn_italic=get_resource_path('fonts/Vollkorn-Italic.ttf'))
LabelBase.register(name = 'CreteRound',
                   fn_regular= get_resource_path('fonts/CreteRound-Regular.ttf'))
LabelBase.register(name = 'Chiller',
                   fn_regular= get_resource_path('fonts/Chiller.ttf'))

# ALL OF THOSE CLASSES ARE DEFINED IN THE KV FILE
class BaseTextLayout(BoxLayout):
    pass

class BaseButtonLayout(BoxLayout):
    pass

class BaseTextLabel(Label):
    pass

class BaseButton(Button):
    pass

class TitleLabel(Label):
    pass

class ImageLayout(BoxLayout):
    pass

class ScreenLayout(BoxLayout):
    pass

class GameTextLayout(BaseTextLayout):
    pass

class GameButtonLayout(BaseButtonLayout):
    pass

class GameLabel(BaseTextLabel):
    pass

class LanguageMenu(Screen):
    pass


class GameScreen(Screen):  # defined in the kv file

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.layout: ScreenLayout = ScreenLayout()  # contains text and button layouts added by place_text() and place_buttons()
        scroll: ScrollView = ScrollView()
        scroll.add_widget(self.layout)
        self.add_widget(scroll)


class GameButton(BaseButton):

    def __init__(self, fate: int, consequences: dict, **kwargs):
        super().__init__(**kwargs)
        self.fate: int = fate
        self.consequences: dict = consequences

class NieblaApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_filename: Optional[str] = None
        self.story: Optional[dict] = None
        self.title: Optional[str] = None
        self.scenes: Optional[list[dict]] = None
        self.all_variables: Optional[dict[str,int]] = None
        self.current_scene: Optional[dict] = None
        self.sm: Optional[ScreenManager] = None

    def build(self) -> ScreenManager:
        self.sm = ScreenManager()
        self.sm.add_widget(LanguageMenu(name="current_screen"))
        self.sm.current = "current_screen"
        return self.sm

    def start_game(self, rel_path: str) -> None:
        self.story = json_utils.read_json(get_resource_path(rel_path))
        self.title = self.story["titulo"]
        self.scenes = json_utils.get_scenes(self.story,
                                            formatted=True)  # removes html tags and introduces kivy markups
        self.all_variables = json_utils.get_variables(self.scenes)
        self.current_scene = json_utils.get_intro(self.scenes)
        self._generate_screen()

    def _generate_screen(self) -> None:

        new_screen = GameScreen(name="current_screen")
        self.place_text_and_images(new_screen)
        self.place_buttons(new_screen)
        self.sm.remove_widget(self.sm.get_screen(self.sm.current))
        self.sm.add_widget(new_screen)

    def place_text_and_images(self, screen: Screen) -> None:

        text_layout = GameTextLayout()

        if self.current_scene['id'] == json_utils.get_intro(self.scenes, id_only=True): #if start of the game, add title
            titledisplay = TitleLabel(text = self.title)
            text_layout.add_widget(titledisplay)

        text_object = json_utils.get_text(self.current_scene)

        for text in text_object:
            conditions = json_utils.get_conditions(text)

            if json_utils.compare_conditions(self.all_variables, conditions):

                if text['texto'][:8] == '[$image]':  # if text is an image
                    display = ImageLayout()  # images must be embedded in BoxLayouts in order to specify padding
                    image_path = get_resource_path('pics/'+ text['texto'][8:])  # image folder must be named 'pics'
                    image_display = Image(source = image_path)  # create Image label
                    display.add_widget(image_display)  # embed Image label in BoxLayout

                else:  # if text is a text
                    display = GameLabel(text=json_utils.align(text['texto'])[0],
                                        halign=json_utils.align(text['texto'])[1])
                
                consequences = json_utils.get_consequences(text)  # consequences are checked for both texts and images
                self.all_variables.update(consequences)
                text_layout.add_widget(display)

        screen.layout.add_widget(text_layout)

    def place_buttons (self, screen: Screen) -> None:

        button_layout = GameButtonLayout()

        text_object = json_utils.get_text(self.current_scene)
        links = json_utils.get_links(text_object[-1])  # links are always in last section of text

        if len(links) == 0:
            intro_id = json_utils.get_intro(self.scenes, id_only=True)
            links = [{'texto': 'Volver a empezar',
                          'destinoExito': intro_id,
                          'consecuencias': [],
                          'condiciones': []}]
            self.all_variables = {key: 0 for key in self.all_variables}  # sets to 0 all variables of the game

        for link in links:
            conditions = json_utils.get_conditions(link)
            if json_utils.compare_conditions(self.all_variables, conditions):    #place button if conditions are met
                button = GameButton(text=link['texto'], fate=link['destinoExito'],
                                    consequences=json_utils.get_consequences(link))
                button.bind(on_release=self.on_button_release)
                button_layout.add_widget(button)

        screen.layout.add_widget(button_layout)

    def on_button_release(self, button: GameButton) -> None:
        self.all_variables.update(button.consequences)
        self.current_scene = json_utils.get_scene(int(button.fate), self.scenes)
        self._generate_screen()


######################################################### START APP ###################################################


if __name__ == '__main__':
    NieblaApp().run()
