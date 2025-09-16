from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widget import Widget
from textual.widgets import Footer, Header, Label, MaskedInput, Input, Placeholder, Static, TabbedContent, TabPane
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual import on
from hackros import HackroGenerator


class HackroMessage(Message):
    """ Custom Message used to communicate between widgets """
    def __init__(self, value: str, id: str) -> None:
        super().__init__()
        self.value = value
        self.id = id
        return 


class HackrosApp(App):
    """ 
    Textual App (Text user interface) to generate Hackros
    i.e. convert user templates into a keystroke format 
    used by elgato stream deck to circumvent
    virtual machine text pasting issues
    """
    
    # will be displayed on the bottom!
    BINDINGS = [
            Binding(
                key='ctrl+n',
                action='add_profile()',
                description='add new profile')
            ]

    def __init__(self):
        self.hgen = HackroGenerator()
        super().__init__()
        return

    # tryna get a callback from input widgets
    def on_hackro_message(self, message: HackroMessage) -> None:
        value = message.value
        if message.id == 'attacker-input':
            target_id = '#attacker-ip'
            msg = f'Attacker IP: {value}'
            token = 'ATTACKER_IP'

        elif message.id == 'victim-ip-input':
            target_id = '#victim-ip'
            msg = f'Victim IP: {value}'
            token = 'VICTIM_IP'

        elif message.id == 'victim-domain-input':
            target_id = '#victim-domain'
            msg = f'Victim Domain: {value}'
            token = 'VICTIM_DOMAIN'

        else:
            # not in the target tab?
            return

        # update ui values
        target = self.query_one(target_id)
        target.update(msg)

        # generate hackros
        self.hgen.tokens[token] = value
        self.hgen.generate_hackro(token)

    # TODO individual css file for live editing
    DEFAULT_CSS = """
    Screen {
        overflow-x: auto;
        overflow-y: auto;
    }
    #app-grid {
        layout: grid;
        grid-size: 2; /* num cols */
        grid-columns: 1fr;
        grid-rows: 2fr;
    }

    /* Target Tab */
    #top-left {
        row-span: 3;
        width: 1fr;
    }
    #target-input-grid {
        layout: grid;
        row-span: 1;
        height: 3fr;
    }
    TabbedContent ContentSwitcher {
        border: solid red;
        height: 1fr;
    }

    /* Profile credential tab */
    #top-right {
        row-span: 3;
        width: 1fr;
    }
    #profile-input-grid {
        layout: grid;
        row-span: 1;
    }

    /* TODO search or sum */
    #bottom {
        column-span: 2;
        row-span: 5;
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Footer()
        yield Header()
        with Container(id='app-grid'):

            # target input
            with Vertical(id='top-left'):
                with TabbedContent():
                    with TabPane('target-input'):
                        with Vertical(id='target-input-grid'):
                            yield LabeledInput('Attacker IP:', id='attacker-input')
                            yield LabeledInput('Victim IP:', id='victim-ip-input')
                            yield LabeledInput('Victim Domain:', id='victim-domain-input')
                        # values
                        with Vertical(id='token-values-grid'):
                            yield Static('Attacker IP: None', id='attacker-ip')
                            yield Static('Victim IP: None', id='victim-ip')
                            yield Static('Victim Domain: None', id='victim-domain')
                    with TabPane('Profile'):
                        yield ProfileTab()

            # profiles with creds
            with Vertical(id='top-right'):
                yield TabbedContent(id='profile-tabs')

            # display command
            with Vertical(id='bottom'):
                yield Placeholder('TODO Search')
    
    # add a new tab?
    def action_add_profile(self) -> None:
        tabs = self.query_one('#profile-tabs')
        new_tab = TabPane('new-test')
        tabs.add_pane(new_tab)
        # get tab name?
        new_tab.mount()

        # set new profile tab
        new_tab.mount(ProfileTab())
        tabs.active = new_tab.id

    def on_mount(self) -> None:
        # header values
        self.title = 'Hackros'
        self.sub_title = 'Template Injection Who?'

class ProfileTab(Widget):
    """ Tab that contains active credential information to be used in hackros """

    def __init__(self) -> None:
        super().__init__()
    
    DEFAULT_CSS = """
    ProfileTab {
        border: solid white;
        height: 1fr;
    }
    
    #profile-input-grid {
        layout: grid;
        row-span: 1;
        height: 3fr; /* Needed to keep labeled input visible??? */
    }

    LabeledInput {
        border: solid green;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Vertical(id='profile-input-grid'):
            yield LabeledInput('Username', id='profile-username-input')
            yield LabeledInput('Password', id='profile-password-input')
            yield LabeledInput('Hash', id='profile-hash-input')
        with Vertical(id='profile-output-grid'):
            yield Static('Username: None', id='profile-username-output')
            yield Static('Password: None', id='profile-password-output')
            yield Static('Hash: None', id='profile-hash-output')
        
    def on_hackro_message(self, msg: HackroMessage) -> None:
        target_id = msg.id
        value = msg.value

        # TODO improve this and make it readable + reusable
        if target_id == 'profile-username-input':
            output_id = '#profile-username-output'
            output_msg = f'Username: {value}'
        elif target_id == 'profile-password-input':
            output_id = '#profile-password-output'
            output_msg = f'Password: {value}'
        elif target_id == 'profile-hash-input':
            output_id = '#profile-hash-output'
            output_msg = f'Hash: {value}'
        else:
            return

        output = self.query_one(output_id)
        output.update(output_msg)


class LabeledInput(Widget):
    """ Label that accepts IP inputs """

    # TODO figure out how to center the label
    DEFAULT_CSS = """
    LabeledInput {
        width: 1fr;
        height: 3fr;
        border: blue;
    }

    #ip-label {
        align: center middle;
        height: 1fr;
    }

    #ip-input {
        width: 1fr;
        height: 2fr;
        border: solid green;
    }

    #ip-grid {
        layout: grid; /* horizontal;*/
        grid-size: 2; /* num cols */
        grid-columns: 1fr 3fr;
        grid-rows: 3;
    }
    """

    def __init__(self, name: str, id: str=None) -> None:
        self.label_name = name
        if id:
            super().__init__(id=id)
        else:
            super().__init__()

    @on(Input.Submitted)
    def submit(self, event: Input.Submitted) -> None:
        ip = event.input.value
        self.post_message(HackroMessage(ip, super().id))

    def compose(self) -> ComposeResult:
        with Container():
            with Horizontal(id='ip-grid'):
                yield Static(self.label_name, id='ip-label')
                yield Input(id='ip-input')

if __name__ == '__main__':
    app = HackrosApp()
    app.run()
