from os import path, remove
import sys
from typing import Optional, LiteralString
from json import dump, load

from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.audio import SoundLoader, Sound

import json_utils
import widgets as wdg
from audio_volumes import get_volume


def get_resource_path(relative_path: str) -> LiteralString | str | bytes:
    """
    Method needed to set the correct path to resources when compiling the app with Pyinstaller
    :param relative_path: relative path to the game file
    :return: the path to the resources
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = path.abspath(".")
    return path.join(base_path, relative_path)

LabelBase.register(name = "Vollkorn",
                   fn_regular= get_resource_path("fonts/Vollkorn-Regular.ttf"),
                   fn_italic=get_resource_path("fonts/Vollkorn-Italic.ttf"))
LabelBase.register(name = "CreteRound",
                   fn_regular= get_resource_path("fonts/CreteRound-Regular.ttf"))
LabelBase.register(name = "Chiller",
                   fn_regular= get_resource_path("fonts/Chiller.ttf"))

class FogApp(App):
    """
    Class defining the game
    """
    soundtrack_name = StringProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_filename: Optional[str] = None
        self.root_layout: Optional[wdg.RootLayout] = None
        self.language: Optional[str] = None
        self.story: Optional[dict] = None
        self.title: Optional[str] = None
        self.scenes: Optional[list[dict]] = None
        self.variables: Optional[dict[str,int]] = None
        self.scene: Optional[dict] = None
        self.soundtrack: Optional[Sound] = None
        # event is triggered by calling play_soundtrack(), never directly
        self.bind(soundtrack_name=self._on_soundtrack_name)

        self.sm: Optional[ScreenManager] = None
        self.interface: Optional[wdg.InterfaceLayout] = None
        self.start_game_transition_time: float = 1.4  # transition duration to the first screen of the game
        self.in_game_transition_time: float = 0.4  # transition duration between screens during game


    def build(self) -> ScreenManager:
        self.root_layout = wdg.RootLayout()
        self.interface = wdg.InterfaceLayout()
        self.sm = ScreenManager(transition=FadeTransition())
        self.root_layout.add_widget(self.sm)
        return self.root_layout

    def get_soundtrack_name(self) -> str:
        """
        Gets the name of the soundtrack of the current scene
        :return: the name of the soundtrack
        """
        return self.scene["soundtrack"]

    def get_scene(self, scene_id:int) -> dict:
        """
        Gets the scene with the passed id from App.scenes
        :param scene_id: id of the scene to get
        :return: scene
        """
        for scene in self.scenes:
            if scene["id"] == scene_id:
                return scene

    def get_scene_location(self) -> str:
        """
        Gets the location of the current scene
        :return: the location of the current scene
        """
        return self.scene["location"]

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

    def _on_soundtrack_name(self, fog_app:App, next_soundtrack_name:Optional[str]) -> None:
        """
        Stops previous soundtrack (if any) and plays next one
        :param fog_app: instance of the app
        :param next_soundtrack_name: soundtrack to be played
        :return: None
        """
        if self.soundtrack is not None:
            self.soundtrack.stop()
            self.soundtrack.unload()
        nst_name = next_soundtrack_name.removesuffix("--in-loop")
        self.soundtrack = SoundLoader.load(f"soundtracks/{nst_name}")
        self.soundtrack.volume = get_volume(nst_name)
        self.soundtrack.loop = True if next_soundtrack_name.endswith("--in-loop") else False
        self.soundtrack.play()

    def play_soundtrack(self, soundtrack_name: str, loop:bool) -> None:
        """
        Starts playing a soundtrack
        :param soundtrack_name: name of the soundtrack to play. Must be in soundtracks/ directory
        :param loop: boolean indicating of soundtrack must play in loop
        :return: None
        """
        if loop:
            soundtrack_name = f"{soundtrack_name}--in-loop"
        self.soundtrack_name = soundtrack_name

    @property
    def check_if_saved_game(self)->bool:
        """
        Checks if there is a saved game
        :return: True if saved game, else False
        """
        return path.exists("saved_game.json")

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
                            "current_scene_id": self.scene["id"]}
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

    def setup_game(self, rel_path: str) -> None:
        """
        Sets up App (game) attributes
        :param rel_path: relative path to the JSON containing the game
        :return: None
        """
        self.story = json_utils.read_json(get_resource_path(rel_path))
        self.title = self.story["title"]
        self.scenes = json_utils.get_scenes(self.story,
                                            formatted=True)  # removes html tags and introduces kivy markups
        self.variables = json_utils.get_variables(self.scenes)

    def start_game(self) -> None:
        """
        Sets up App attributes and generates the first screen of the game
        :return: None
        """
        self.scene = json_utils.get_intro(self.scenes)
        self._launch_game()

    def load_game(self) -> None:
        """
        Overwrites the game state according to the saved_game.json file and generates the first screen of loaded game
        :return: None
        """
        with open("saved_game.json","r") as f:
            game_state: dict = load(f)

        self.variables = game_state["variables"]
        self.scene = self.get_scene(game_state["current_scene_id"])
        self._launch_game()

    def _launch_game(self) -> None:
        """
        Launches the game and shows the first screen
        :return: None
        """
        self.play_soundtrack(self.get_soundtrack_name(), loop=True)
        self.interface.set_localtionlabel_text(self.get_scene_location())
        self.show_interface_bar()
        self.show_gamescreen(self.start_game_transition_time, height_subtract=self.interface.height)

    def show_interface_bar(self) -> None:
        """
        Adds the interface button bar on top of the screen
        :return: None
        """
        self.root_layout.remove_widget(self.sm)
        self.root_layout.add_widget(self.interface)
        self.root_layout.add_widget(self.sm)

    def remove_interface_bar(self) -> None:
        """
        Removes the interface from the screen
        :return: None
        """
        self.root_layout.remove_widget(self.interface)

    def show_start_menu(self) -> None:
        """
        Assembles the game start menu and displays it
        :return: None
        """
        self.sm.remove_widget(self.sm.get_screen("current_screen"))
        self.sm.add_widget(wdg.StartMenu(name="current_screen"))

    def show_gamescreen(self, transition_duration: float, height_subtract: Optional[float] = None) -> None:
        """
        Assembles the next game screen and displays it
        :param transition_duration: duration in seconds of the transition
        :param height_subtract: height to subtract to avoid collision of GamesScren with interfaces when fading in
        :return: None
        """
        next_screen = wdg.GameScreen(name="next_screen", height_subtract=height_subtract)
        self.place_text_and_images(next_screen)
        self.place_gamebuttons(next_screen)
        self._transition_screen(next_screen, transition_duration)

    def _transition_screen(self, next_screen: wdg.Screen, duration: float) -> None:
        """
        Transitions softly from the current screen to the next screen
        :param next_screen: next screen to be displayed
        :param duration: duration in seconds of the transition
        :return: None
        """
        self.sm.transition.duration = duration
        self.sm.add_widget(next_screen)
        # self.sm.get_screen("current_screen").opacity = 0  # uncomment this to supress fading out of current_screen
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
        sections: list[dict] = json_utils.get_sections(self.scene)

        for section in sections:
            conditions: dict = json_utils.get_conditions(section)

            if json_utils.compare_conditions(self.variables, conditions):

                if section["text"][:8] == "[$image]":  # if image
                    game_resource: wdg.ImageLayout = self._assemble_gameimage(img_path="pics/" + section["text"][8:])

                else:  # if text
                    game_resource: wdg.GameTextLabel = self._assemble_gametext(json_utils.align(section["text"]))
                
                consequences: dict = json_utils.get_consequences(section)  # consequences checked for both texts and images
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
        game_obj: list[dict] = json_utils.get_sections(self.scene)
        links: list[dict] = json_utils.get_links(game_obj[-1])  # links are always found in last index of game_obj

        if len(links) == 0:  # if no links (end game)
            startmenubutton = self._assemble_startmenubutton(self.language)
            layout.add_widget(startmenubutton)

        #else
        for link in links:
            conditions:dict = json_utils.get_conditions(link)

            if json_utils.compare_conditions(self.variables, conditions):    #place button if conditions are met
                gamebutton: wdg.GameButton = self._assemble_gamebutton(text=link["text"],
                                                                   destination_scene_id=link["destination_scene_id"],
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
        self.scene: dict = self.get_scene(button.destination_scene_id)
        self.play_soundtrack(self.get_soundtrack_name(), loop=True)
        self.save_game()
        self.interface.set_localtionlabel_text(self.get_scene_location())
        self.show_gamescreen(self.in_game_transition_time)

    def on_startmenubutton_release(self, button: wdg.GameButton) -> None:
        """
        Controls what happens when a StartMenuButton is activated. Must be implemented here within FogApp
        class because it needs to FogApp.variables and FogApp.current_scene.
        :param button: instance of the button activated
        :return: None
        """
        self.remove_interface_bar()
        self.reset_variables()
        self.delete_saved_game()
        self.play_soundtrack("opening.mp3", loop=False)
        self.show_start_menu()

    @staticmethod
    def _assemble_gametext(game_obj_section: dict) -> wdg.GameTextLabel:
        """
        Assembles a TextLabel with the game text at leaves it ready to place in the GameLayout
        :param game_obj_section: section from the game_obj the text to display
        :return: GameTextLabel instance containing the text
        """
        return wdg.GameTextLabel(text=game_obj_section[0], halign=game_obj_section[1])

    def _assemble_gamebutton(self, text: str, destination_scene_id: int, consequences: dict) -> wdg.GameButton:
        """
        Assembles a GameButton and leaves it ready to place in the ButtonLayout
        :param text: text of the GameButton
        :param destination_scene_id: section id where GameButton leads when pressed
        :param consequences: consequences of the pressing of the GameButton
        :return: GameButton instance
        """
        gamebutton = wdg.GameButton(text=text, destination_scene_id=destination_scene_id, consequences=consequences)
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
