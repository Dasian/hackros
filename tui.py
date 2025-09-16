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
        height: 4fr; /* needed to keep input visible - don't ask */
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

            # TODO maybe make creds a tab here?
            # target input
            with Vertical(id='top-left'):
                with TabbedContent(id='targets'):
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

            # profiles with creds
            with Vertical(id='top-right'):
                with TabbedContent(id='profile-tabs'):
                    with TabPane('creds1'):
                        yield ProfileTab(self.hgen)

            # display command
            with Vertical(id='bottom'):
                yield Placeholder('TODO Search')
    
    # add a new tab?
    def action_add_profile(self) -> None:
        tabs = self.query_one('#profile-tabs')

        # TODO get tab name?

        # create new tab
        new_tab = TabPane(f'creds-{tabs.tab_count + 1}')
        tabs.add_pane(new_tab)
        new_tab.mount()

        # set tab content to profile widget
        new_tab.mount(ProfileTab(self.hgen))
        # tbh idk what value this is...
        tabs.active = new_tab.id

    def on_mount(self) -> None:
        # header values
        self.title = 'Hackros'
        self.sub_title = 'Template Injection Who?'

class ProfileTab(Widget):
    """ Tab that contains active credential information to be used in hackros """

    def __init__(self, hgen: HackroGenerator, tokens: dict={}) -> None:
        self.hgen = hgen
        # list of profile tokens supported
        self.valid_tokens = self.hgen.valid_profile_tokens
        self.tokens = tokens

        # fill default values
        if not tokens:
            for tok in self.valid_tokens:
                self.tokens[tok] = tok

        super().__init__()
    
    DEFAULT_CSS = """
    ProfileTab {
        border: solid white;
        height: 1fr;
    }
    
    #profile-input-grid {
        layout: grid;
        row-span: 1;
        height: 6fr; /* Needed to keep labeled input visible??? */
    }

    LabeledInput {
        border: solid green;
    }
    """
    
    def compose(self) -> ComposeResult:
        # profile inputs
        with Vertical(id='profile-input-grid'):
            for tok in self.tokens.keys():
                yield LabeledInput(f'{tok}', id=f'{tok}')

        # profile outputs
        with Vertical(id='profile-output-grid'):
            for tok in self.tokens.keys():
                yield Static(f'{tok}: None', id=f'{tok}-output')

    # updates the profile/multiple token hackros when
    # an input is received
    def on_hackro_message(self, msg: HackroMessage) -> None:
        token = msg.id
        value = msg.value

        if token not in self.valid_tokens:
            return

        # update profile output
        output_id = f'#{token}-output'
        output_msg = f'{token}: {value}'
        output = self.query_one(output_id)
        output.update(output_msg)

        # update profile backend
        self.hgen.update_profile(self.id, token, value)


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
