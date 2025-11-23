from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen


# ALL THOSE CLASSES ARE DEFINED IN THE KV FILE
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
