from typing import Optional

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.metrics import dp


# ALL EMPTY CLASSES ARE DEFINED IN THE KV FILE. THE OTHERS MAY BE EXTENDED THERE AS WELL
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

class BaseButton(Button):
    """
    Base Button
    """
    pass

class FadingLabel(Label):
    """
    Label that fades in. Event may be bound on_complete (when fading is completed)
    :return: None
    """
    def __init__(self, on_complete: Optional[callable] = None, **kwargs):
        super().__init__(**kwargs)
        self.opacity: float = 0.0  # start invisible
        self.on_complete: Optional[callable] = on_complete
        if getattr(self, "duration", None) is None:
            raise NotImplementedError("All FadingLabel child classes must define 'duration' attribute")

    def _fade_in(self) -> None:
        """
        Handles the fading in of the FadingLabel
        :return: None
        """
        fading = Animation(opacity=1.0, duration=self.duration, transition="in_quad")
        if self.on_complete is not None:
            fading.bind(on_complete=self.on_complete)
        fading.start(self)

class TitleLabel(FadingLabel):
    """
    Special Label for displaying the title of the Game in the StartMenu
    """
    def __init__(self, **kwargs):
        self.duration: float = 4.0  # must be defined before super() to avoid NotImplementedError
        super().__init__(**kwargs)
        self._fade_in()

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

class GameTextLabel(Label):
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
    Screen displaying the game start menu
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation="vertical")
        self.text_image_layout = BaseTextImageLayout(padding=(dp(0), dp(70), dp(0), dp(0)))
        self.button_layout = BaseButtonLayout()
        self.main_layout.add_widget(self.text_image_layout)
        self.main_layout.add_widget(self.button_layout)
        self.add_widget(self.main_layout)
        self.text_image_layout.add_widget(TitleLabel(on_complete=self._show_buttons))

    def _show_buttons(self, animation: Animation, title_label: TitleLabel) -> None:
        """
        Shows the Buttons of the StartMenu
        :param animation: fading animation of the TitleLabel
        :param title_label: TitleLabel instance
        :return: None
        """
        self.button_layout.add_widget(StartGameButton())
        self.button_layout.add_widget(ContinueGameButton())

class GameScreen(Screen):  # defined in the kv file
    """
    Class defining the Screen showing the game, consisting of a ScreenLayout embedded in an ScrollView
    """
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.layout: ScreenLayout = ScreenLayout()  # contains text and button layouts added by place_text() and place_buttons()
        scroll: ScrollView = ScrollView()
        scroll.add_widget(self.layout)
        self.add_widget(scroll)
