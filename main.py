from os import path, remove
import sys
from typing import Optional, LiteralString
from json import dump, load

from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager, FadeTransition

import json_utils
import widgets as wdg

def get_resource_path(relative_path: str) -> LiteralString | str | bytes:
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

class FogApp(App):
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
        self.sm = ScreenManager(transition=FadeTransition(duration=0.35))
        return self.sm

    def on_start(self) -> None:
        """
        Schedules app launch in 1 second to avoid black screen issue during app launching on Android.
        See the following GitHub issue for more info: https://github.com/kivy/python-for-android/issues/2720
        :return: None
        """
        Clock.schedule_once(self._launch_app, 1)

    def _launch_app(self, dt) -> None:
        """
        This delayed start ensures no frozen black screen when launching the app
        :param dt: delta time
        :return: None
        """
        self.sm.add_widget(wdg.LanguageMenu(name="current_screen"))
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
        game_state: dict = {"variables": self.variables,
                            "current_scene_id": self.current_scene["id"]}
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
        self.show_gamescreen()

    def setup_game(self, rel_path: str) -> None:
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

    def start_game(self) -> None:
        """
        Sets up App attributes and generates the first screen of the game
        :return: None
        """
        self.current_scene = json_utils.get_intro(self.scenes)
        self.show_gamescreen()

    def show_start_menu(self) -> None:
        """
        Assembles the game start menu and displays it
        :return: None
        """
        self.sm.remove_widget(self.sm.get_screen("current_screen"))
        self.sm.add_widget(wdg.StartMenu(name="current_screen"))

    def show_gamescreen(self) -> None:
        """
        Assembles the next game screen and displays it
        :return: None
        """
        next_screen = wdg.GameScreen(name="next_screen")
        self.place_text_and_images(next_screen)
        self.place_gamebuttons(next_screen)
        self._transition_screen(next_screen)

    def _transition_screen(self, next_screen: wdg.Screen) -> None:
        """
        Transitions softly from the current screen to the next screen
        :param next_screen: next screen to be displayed
        :return: None
        """
        self.sm.add_widget(next_screen)
        self.sm.current = "next_screen"
        self.sm.remove_widget(self.sm.get_screen("current_screen"))
        self.sm.get_screen("next_screen").name = "current_screen"

    def place_text_and_images(self, screen: wdg.Screen) -> None:
        """
        Wrapper to generate GameTextLabel and GameImage and organize them in their GameTextImageLayout
        :param screen: Screen in which the text and images must be placed
        :return: None
        """
        layout = wdg.GameTextImageLayout()
        game_obj: dict = json_utils.get_text(self.current_scene)

        for obj in game_obj:
            conditions: dict = json_utils.get_conditions(obj)

            if json_utils.compare_conditions(self.variables, conditions):

                if obj["texto"][:8] == "[$image]":  # if image
                    game_resource: wdg.ImageLayout = self._assemble_gameimage(img_path="pics/" + obj["texto"][8:])

                else:  # if text
                    game_resource: wdg.GameTextLabel = self._assemble_gametext(json_utils.align(obj["texto"]))
                
                consequences: dict = json_utils.get_consequences(obj)  # consequences checked for both texts and images
                self.variables.update(consequences)
                layout.add_widget(game_resource)

        screen.layout.add_widget(layout)

    def place_gamebuttons (self, screen: wdg.Screen) -> None:
        """
        Wrapper method to generate GameButtons and organize them in their GameButtonLayout
        :param screen: Screen in which the GameButtons must be placed
        :return: None
        """
        layout = wdg.GameButtonLayout()
        game_obj: dict = json_utils.get_text(self.current_scene)
        links: list[dict] = json_utils.get_links(game_obj[-1])  # links are always found in last index of game_obj

        if len(links) == 0:  # if no links (end game)
            startmenubutton = self._assemble_startmenubutton(self.language)
            layout.add_widget(startmenubutton)

        #else
        for link in links:
            conditions:dict = json_utils.get_conditions(link)

            if json_utils.compare_conditions(self.variables, conditions):    #place button if conditions are met
                gamebutton: wdg.GameButton = self._assemble_gamebutton(text=link["texto"],
                                                                   fate=link["destinoExito"],
                                                                   consequences=json_utils.get_consequences(link))
                layout.add_widget(gamebutton)

        screen.layout.add_widget(layout)

    def on_gamebutton_release(self, button: wdg.GameButton) -> None:
        """
        Controls what happens when a GameButton is activated. Must be implemented here within FogApp class because
        it needs to FogApp.variables and FogApp.current_scene.
        :param button: instance of the button activated
        :return: None
        """
        self.variables.update(button.consequences)
        self.current_scene: dict = self.get_scene(int(button.fate))
        self.save_game()
        self.show_gamescreen()

    def on_startmenubutton_release(self, button: wdg.GameButton) -> None:
        """
        Controls what happens when a StartMenuButton is activated. Must be implemented here within FogApp
        class because it needs to FogApp.variables and FogApp.current_scene.
        :param button: instance of the button activated
        :return: None
        """
        self.reset_variables()
        self.delete_saved_game()
        self.show_start_menu()

    @staticmethod
    def _assemble_gametext(game_obj_section: dict) -> wdg.GameTextLabel:
        """
        Assembles a TextLabel with the game text at leaves it ready to place in the GameLayout
        :param game_obj_section: section from the game_obj the text to display
        :return: GameTextLabel instance containing the text
        """
        return wdg.GameTextLabel(text=game_obj_section[0], halign=game_obj_section[1])

    def _assemble_gamebutton(self, text: str, fate: int, consequences: dict) -> wdg.GameButton:
        """
        Assembles a GameButton and leaves it ready to place in the ButtonLayout
        :param text: text of the GameButton
        :param fate: section id where GameButton leads when pressed
        :param consequences: consequences of the pressing of the GameButton
        :return: GameButton instance
        """
        gamebutton = wdg.GameButton(text=text, fate=fate, consequences=consequences)
        gamebutton.bind(on_release=self.on_gamebutton_release)
        return gamebutton

    def _assemble_startmenubutton(self, language: str) -> wdg.StartMenuButton:
        """
        Assembles a StartMenuButton at leaves it ready to place in the ButtonLayout
        :param language: language of the StartMenuButton text
        :return: StartMenuButton instance
        """
        startmenubutton = wdg.StartMenuButton(language)
        startmenubutton.bind(on_release=self.on_startmenubutton_release)
        return startmenubutton

    @staticmethod
    def _assemble_gameimage(img_path: str) -> wdg.ImageLayout:
        """
        Assembles a GameImage at leaves it ready to place in the GameLayout
        :param img_path: path to the png image
        :return: the Image embedded in its own ImageLayout
        """
        layout = wdg.ImageLayout()  # images must be embedded in BoxLayouts in order to specify padding
        image_path = get_resource_path(img_path)  # image folder must be named "pics"
        gameimage = wdg.GameImage(source=image_path)
        layout.add_widget(gameimage)
        return layout

######################################################### START APP ###################################################

if __name__ == '__main__':
    FogApp().run()
