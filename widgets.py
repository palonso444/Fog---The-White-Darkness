from typing import Optional

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation


# ALL EMPTY CLASSES ARE DEFINED IN THE KV FILE. THE OTHERS MAY BE EXTENDED THERE AS WELL
# BASE CLASSES SHOULD NOT BE INSTANTIATED
class BaseButtonLayout(BoxLayout):
    """
    Base Layout buttons
    """
    pass

class BaseButton(Button):
    """
    Base Button
    """
    pass

class FadingMixin:
    """
    Mixin class that adds fading capabilities to Widget subclasses.
    Event may be bound on_fading_complete. Usage example -> class TitleLabel(FadingMixin, Label):
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_fading_complete = None
        if getattr(self, "duration", None) is None:
            raise AttributeError("All FadingMixin child classes must define 'duration' attribute "
                                 "before calling super()")

    def _fade_in(self, duration: float) -> None:
        """
        Handles the fading in of the FadingLabel
        :param duration: duration in seconds of the fading
        :return: None
        """
        fading = Animation(opacity=1.0, duration=duration, transition="in_quad")
        if self.on_fading_complete is not None:
            fading.bind(on_complete=self.on_fading_complete)
        fading.start(self)

class TitleLabel(FadingMixin, Label):
    """
    Special Label for displaying the title of the Game in the StartMenu
    """
    def __init__(self, on_fading_complete: Optional[callable] = None, **kwargs):
        self.duration: float = 4.0  # must be defined before super() to avoid AttributeError
        super().__init__(**kwargs)
        self.on_fading_complete = on_fading_complete
        self._fade_in(self.duration)

class GameImage(Image):
    """
    Displays in-game images
    """
    pass

class RootLayout(BoxLayout):
    """
    Root layout for all the app
    """
    pass

class StartMenuLayout(BoxLayout):
    """
    General layout for StartMenu
    """
    pass

class TitleLayout(BoxLayout):
    """
    Layout for game title in StartMenu
    """
    pass

class StartMenuButtonLayout(BaseButtonLayout):
    """
    Layout for buttons of StartMenu
    """
    pass

class InterfaceLayout(BoxLayout):
    """
    Layout for game interface buttons
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

class GameTextImageLayout(BoxLayout):
    """
    Layout for in-game texts and images, adapted to ScrollView
    """
    pass

class GameButtonLayout(BaseButtonLayout):
    """
    Layout for in-game buttons, adapted to ScrollView
    """
    pass

class GameTextLabel(Label):
    """
    Label for in-game texts
    """
    pass

class CopyrightLabel(Label):
    """
    Label for displaying copyright message at StartMenu
    """
    pass

class GameButton(BaseButton):
    """
    Buttons displayed during the game, not in the Menus
    """
    def __init__(self, destination_scene_id: int, consequences: dict, **kwargs):
        super().__init__(**kwargs)
        self.destination_scene_id: int = destination_scene_id
        self.consequences: dict = consequences

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

class LanguageMenu(Screen):
    """
    Screen displaying the language selection menu
    """
    pass

class StartMenu(Screen):
    """
    Screen displaying the game start menu
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = StartMenuLayout(orientation="vertical")
        self.title_layout = TitleLayout()
        self.button_layout = StartMenuButtonLayout()
        self.main_layout.add_widget(self.title_layout)
        self.main_layout.add_widget(self.button_layout)
        self.add_widget(self.main_layout)
        self.title_layout.add_widget(TitleLabel(on_fading_complete=self._show_buttons))

    def _show_buttons(self, animation: Animation, title_label: TitleLabel) -> None:
        """
        Shows the Buttons of the StartMenu
        :param animation: fading animation of the TitleLabel
        :param title_label: TitleLabel instance
        :return: None
        """
        self.button_layout.add_widget(StartGameButton())
        self.button_layout.add_widget(ContinueGameButton())
        self.button_layout.add_widget(CopyrightLabel())

class GameScreen(Screen):  # defined in the kv file
    """
    Class defining the Screen showing the game, consisting of a ScreenLayout embedded in an ScrollView
    """
    def __init__(self, height_subtract: Optional[float], **kwargs):
        super().__init__(**kwargs)
        self.height_subtract: Optional[float] = height_subtract
        self.layout: ScreenLayout = ScreenLayout()  # contains text and button layouts added by place_text() and place_buttons()
        scroll: ScrollView = ScrollView()
        scroll.add_widget(self.layout)
        self.add_widget(scroll)

        if self.height_subtract is not None:
            self.bind(on_pre_enter=self._subtract_height)

    def _subtract_height(self, *args) -> None:
        """
        Adjust the height of the GameScreen before FadingTransition starts to avoid interference with the upper
        interface bar
        :param args: Added for consistency, nothing is actually passed
        :return: None
        """
        self.height -= self.height_subtract / 1.83  # adjusting factor not sure the reason why

