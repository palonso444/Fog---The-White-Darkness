from os import path, remove
import sys
from typing import Optional, LiteralString
from json import dump, load

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.text import LabelBase
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen

import json_utils

def get_resource_path(relative_path) -> LiteralString | str | bytes:
    """
    Method needed to set the correct path to resources when compiling the app with Pyinstaller
    :param relative_path: relative path to the game file
    :return: the path to the resources
    """
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
class BaseTextImageLayout(BoxLayout):
    """
    Base Layout for texts and images
    """
    pass

class BaseButtonLayout(BoxLayout):
    """
    Base Layout buttons
    """
    pass

class BaseTextLabel(Label):
    """
    Base Label for texts
    """
    pass

class BaseButton(Button):
    """
    Base Button
    """
    pass

class TitleLabel(Label):
    """
    Special Label for displaying the title of the Game in the StartMenu
    """
    pass

class GameImage(Image):
    """
    Displays in-game images
    """
    pass

class ImageLayout(BoxLayout):
    """
    Layout for embedding individual in-game images
    """
    pass

class ScreenLayout(BoxLayout):
    """
    General Layout for GameScreens, contains GameTextImageLayout and GameButtonLayout
    """
    pass

class GameTextImageLayout(BaseTextImageLayout):
    """
    Layout for in-game texts and images, adapted to ScrollView
    """
    pass

class GameButtonLayout(BaseButtonLayout):
    """
    Layout for in-game buttons, adapted to ScrollView
    """
    pass

class GameText(BaseTextLabel):
    """
    Label for in-game texts
    """
    pass

class MenuButton(BaseButton):
    """
    Base Class for Buttons shown in menus
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not callable(getattr(self, "get_text", None)):
            raise NotImplementedError("All MenuButton child classes must implement 'get_text' method")

    @staticmethod
    def get_text(language: str) -> str:
        """
        Method returning the text of the MenuButton based on the language argument
        (language selected in the LanguageMenu). Must be implemented in all child classes
        :param language: selected language
        :return: the text of the button
        """
        pass

class StartGameButton(MenuButton):
    """
    Button stating (or restarting) the game
    """
    @staticmethod
    def get_text(language: str) -> str:
        """
        See parent method docstring
        """
        match language:
            case "english":
                return "Start"
            case "spanish":
                return "Empezar"
            case _:
                raise ValueError(f"Invalid language argument '{language}'")

class ContinueGameButton(MenuButton):
    """
    Button loading previous game
    """
    @staticmethod
    def get_text(language: str) -> str:
        """
        See parent method docstring
        """
        match language:
            case "english":
                return "Continue"
            case "spanish":
                return "Continuar"
            case _:
                raise ValueError(f"Invalid language argument '{language}'")

class StartMenuButton(MenuButton):
    """
    Button leading to StartMenu
    """
    def __init__(self, language: str, **kwargs):
        super().__init__(**kwargs)
        self.text: str = self.get_text(language)

    @staticmethod
    def get_text(language: str) -> str:
        """
        See parent method docstring
        """
        match language:
            case "english":
                return "Restart"
            case "spanish":
                return "Volver a empezar"
            case _:
                raise ValueError(f"Invalid language argument '{language}'")

class GameButton(BaseButton):
    """
    Buttons displayed during the game, not in the Menus
    """
    def __init__(self, fate: int, consequences: dict, **kwargs):
        super().__init__(**kwargs)
        self.fate: int = fate
        self.consequences: dict = consequences

class LanguageMenu(Screen):
    """
    Screen displaying the language selection menu
    """
    pass

class StartMenu(Screen):
    """
    Screen displaying the language selection menu
    """
    pass

class GameScreen(Screen):  # defined in the kv file
    """
    Class defining the Screes of the game, consisting of a ScreenLayout embedded in an ScrollView
    """
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.layout: ScreenLayout = ScreenLayout()  # contains text and button layouts added by place_text() and place_buttons()
        scroll: ScrollView = ScrollView()
        scroll.add_widget(self.layout)
        self.add_widget(scroll)

class NieblaApp(App):
    """
    Class defining the game
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_filename: Optional[str] = None
        self.language: Optional[str] = None
        self.story: Optional[dict] = None
        self.title: Optional[str] = None
        self.scenes: Optional[list[dict]] = None
        self.variables: Optional[dict[str,int]] = None
        self.current_scene: Optional[dict] = None
        self.sm: Optional[ScreenManager] = None

    def build(self) -> ScreenManager:
        self.sm = ScreenManager()
        return self.sm

    def on_start(self) -> None:
        """
        Schedules app launch (works even at 0 seconds) to avoid black screen issue during app launching on Android.
        See the following GitHub issue for more info: https://github.com/kivy/python-for-android/issues/2720
        :return: None
        """
        Clock.schedule_once(self.launch_app, 0)

    def launch_app(self, dt) -> None:
        """
        This delayed start ensures no frozen black screen when launching the app
        :param dt: delta time
        :return: None
        """
        self.sm.add_widget(LanguageMenu(name="current_screen"))
        self.sm.current = "current_screen"

    @property
    def check_if_saved_game(self)->bool:
        """
        Checks if there is a saved game
        :return: True if saved game, else False
        """
        return path.exists("saved_game.json")

    def get_scene(self, scene_id:int) -> dict:
        """
        Gets the scene with the passed id from App.scenes
        :param scene_id: id of the scene to get
        :return: scene
        """
        for scene in self.scenes:
            if scene['id'] == scene_id:
                return scene

    def reset_variables(self) -> None:
        """
        Resets all variables of the game
        :return: None
        """
        self.variables = {key: 0 for key in self.variables}

    def save_game(self) -> None:
        """
        Gets the game state and saves the game
        :return: None
        """
        game_state = dict()
        game_state["variables"] = self.variables
        game_state["current_scene_id"] = self.current_scene["id"]
        with open("saved_game.json", "w") as f:
            dump(game_state, f, indent=4)

    @staticmethod
    def delete_saved_game() -> None:
        """
        Deletes the saved_game.json file
        :return: None
        """
        if path.exists("saved_game.json"):
            remove("saved_game.json")

    def load_game(self) -> None:
        """
        Overwrites the game state according to the saved_game.json file and generates the first screen of loaded game
        :return: None
        """
        with open("saved_game.json","r") as f:
            game_state: dict = load(f)

        self.variables = game_state["variables"]
        self.current_scene = self.get_scene(game_state["current_scene_id"])
        self._generate_screen()

    def setup_game(self, rel_path) -> None:
        """
        Sets up App (game) attributes
        :param rel_path: relative path to the JSON containing the game
        :return: None
        """
        self.story = json_utils.read_json(get_resource_path(rel_path))
        self.title = self.story["titulo"]
        self.scenes = json_utils.get_scenes(self.story,
                                            formatted=True)  # removes html tags and introduces kivy markups
        self.variables = json_utils.get_variables(self.scenes)

    def show_start_menu(self) -> None:
        """
        Shows the game Start Menu
        :return: None
        """
        new_screen = StartMenu(name="current_screen")
        self.sm.remove_widget(self.sm.get_screen(self.sm.current))
        self.sm.add_widget(new_screen)

    def start_game(self) -> None:
        """
        Sets up App attributes and generates the first screen of the game
        :return: None
        """
        self.current_scene = json_utils.get_intro(self.scenes)
        self._generate_screen()

    def place_text_and_images(self, screen: Screen) -> None:
        """
        Wrapper to generate GameText and GameImage and organize them in their GameTextImageLayout
        :param screen: Screen in which the text and images must be placed
        :return: None
        """
        layout = GameTextImageLayout()
        game_obj: dict = json_utils.get_text(self.current_scene)

        for obj in game_obj:
            conditions: dict = json_utils.get_conditions(obj)

            if json_utils.compare_conditions(self.variables, conditions):

                if obj["texto"][:8] == "[$image]":  # if image
                    game_resource:ImageLayout = self._assemble_gameimage(img_path="pics/" + obj["texto"][8:])

                else:  # if text
                    game_resource:GameText = self._assemble_gametext(json_utils.align(obj["texto"]))
                
                consequences: dict = json_utils.get_consequences(obj)  # consequences checked for both texts and images
                self.variables.update(consequences)
                layout.add_widget(game_resource)

        screen.layout.add_widget(layout)

    def place_gamebuttons (self, screen: Screen) -> None:
        """
        Wrapper method to generate GameButtons and organize them in their GameButtonLayout
        :param screen: Screen in which the GameButtons must be placed
        :return: None
        """
        layout = GameButtonLayout()
        game_obj: dict = json_utils.get_text(self.current_scene)
        links: list[dict] = json_utils.get_links(game_obj[-1])  # links are always found in last index of game_obj

        if len(links) == 0:  # if no links (end game)
            startmenubutton = self._assemble_startmenubutton(self.language)
            layout.add_widget(startmenubutton)

        #else
        for link in links:
            conditions:dict = json_utils.get_conditions(link)

            if json_utils.compare_conditions(self.variables, conditions):    #place button if conditions are met
                gamebutton: GameButton = self._assemble_gamebutton(text=link["texto"],
                                                                   fate=link["destinoExito"],
                                                                   consequences=json_utils.get_consequences(link))
                layout.add_widget(gamebutton)

        screen.layout.add_widget(layout)

    def on_gamebutton_release(self, button: GameButton) -> None:
        """
        Controls what happens when a GameButton is activated. Must be implemented here within NieblaApp class because
        it needs to NieblaApp.variables and NieblaApp.current_scene.
        :param button: instance of the button activated
        :return: None
        """
        self.variables.update(button.consequences)
        self.current_scene: dict = self.get_scene(int(button.fate))
        self.save_game()
        self._generate_screen()

    def on_startmenubutton_release(self, button: GameButton) -> None:
        """
        Controls what happens when a StartMenuButton is activated. Must be implemented here within NieblaApp
        class because it needs to NieblaApp.variables and NieblaApp.current_scene.
        :param button: instance of the button activated
        :return: None
        """
        self.reset_variables()
        self.delete_saved_game()
        self.show_start_menu()

    def _generate_screen(self) -> None:
        """
        Generates a new game screen and places it to the ScreenManager
        :return: None
        """
        new_screen = GameScreen(name="current_screen")
        self.place_text_and_images(new_screen)
        self.place_gamebuttons(new_screen)
        self.sm.remove_widget(self.sm.get_screen(self.sm.current))
        self.sm.add_widget(new_screen)

    @staticmethod
    def _assemble_gametext(game_obj_section: dict) -> GameText:
        """
        Assembles a TextLabel with the game text at leaves it ready to place in the GameLayout
        :param game_obj_section: section from the game_obj the text to display
        :return: GameText instance containing the text
        """
        return GameText(text=game_obj_section[0], halign=game_obj_section[1])

    def _assemble_gamebutton(self, text: str, fate: int, consequences: dict) -> GameButton:
        """
        Assembles a GameButton and leaves it ready to place in the ButtonLayout
        :param text: text of the GameButton
        :param fate: section id where GameButton leads when pressed
        :param consequences: consequences of the pressing of the GameButton
        :return: GameButton instance
        """
        gamebutton = GameButton(text=text, fate=fate, consequences=consequences)
        gamebutton.bind(on_release=self.on_gamebutton_release)
        return gamebutton

    def _assemble_startmenubutton(self, language: str) -> StartMenuButton:
        """
        Assembles a StartMenuButton at leaves it ready to place in the ButtonLayout
        :param language: language of the StartMenuButton text
        :return: StartMenuButton instance
        """
        startmenubutton = StartMenuButton(language)
        startmenubutton.bind(on_release=self.on_startmenubutton_release)
        return startmenubutton

    @staticmethod
    def _assemble_gameimage(img_path: str) -> ImageLayout:
        """
        Assembles a GameImage at leaves it ready to place in the GameLayout
        :param img_path: path to the png image
        :return: the Image embedded in its own ImageLayout
        """
        layout = ImageLayout()  # images must be embedded in BoxLayouts in order to specify padding
        image_path = get_resource_path(img_path)  # image folder must be named "pics"
        gameimage = GameImage(source=image_path)
        layout.add_widget(gameimage)
        return layout

######################################################### START APP ###################################################

if __name__ == '__main__':
    NieblaApp().run()
