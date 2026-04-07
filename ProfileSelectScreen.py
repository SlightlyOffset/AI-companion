import os

from textual.app import ComposeResult, App
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Header, Label, ListView, Footer, ListItem


class ProfileSelect(Screen):
    """Screen for selecting character and user profiles."""
    PROFILES_DIR = "profiles"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="selection_container"):
            yield Label("Welcome to [bold magenta]t.ai[/bold magenta]", id="welcome_label")
            yield Label("Select a Character Profile:", id="selection_label")
            yield ListView(id="character_list")
        yield Footer()

    def on_mount(self) -> None:
        """Load available profiles and display them in the ListView."""
        if os.path.exists(self.PROFILES_DIR):
            profiles = [f for f in os.listdir(self.PROFILES_DIR) if f.endswith(".json")]
            for profile in profiles:
                display_name = profile.replace(".json", "").replace("_", " ").title()
                self.query_one("#character_list").append(ListItem(Label(display_name), name=profile))

class TaiApp(App):
    """The t.ai Terminal Application."""
    TITLE = "t.ai"
    SUBTITLE = "Terminal AI Companion"
    # CSS_PATH = "menu.tcss"

    def on_mount(self) -> None:
        self.push_screen(ProfileSelect())

if __name__ == "__main__":
    app = TaiApp()
    app.run()