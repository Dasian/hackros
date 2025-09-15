from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widget import Widget
from textual.widgets import Footer, Header, Label, MaskedInput, Input, Placeholder, Static
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

    # TODO individual css file for live editing
    DEFAULT_CSS = """
    #app-grid {
        layout: grid;
        grid-size: 2; /* num cols */
        grid-columns: 1fr 1fr;
        grid-rows: 1fr;
    }
    #top-left {
        layout: grid;
        row-span: 3;
        width: 1fr;
    }
    #token-values-grid {
        layout: grid;
        row-span: 1;
    }
    #top-right {
        row-span: 3;
    }
    #bottom {
        column-span: 2;
        row-span: 1;
    }
    #token-values-grid > Static {
        height: 2;
        background: blue;
    }
    """

    # will be displayed on the bottom!
    BINDINGS = [
            Binding(
                key='q', 
                action='quit', 
                description='quit the app')
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

        # update ui values
        target = self.query_one(target_id)
        target.update(msg)

        # generate hackros
        self.hgen.tokens[token] = value
        self.hgen.generate_hackro(token)

    def compose(self) -> ComposeResult:
        yield Footer()
        yield Header()
        with Container(id='app-grid'):
            # input
            with Vertical(id='top-left'):
                yield LabeledInput('Attacker IP:', id='attacker-input')
                yield LabeledInput('Victim IP:', id='victim-ip-input')
                yield LabeledInput('Victim Domain:', id='victim-domain-input')
                # values
                with Vertical(id='token-values-grid'):
                    yield Static('Attacker IP: None', id='attacker-ip')
                    yield Static('Victim IP: None', id='victim-ip')
                    yield Static('Victim Domain: None', id='victim-domain')

            # search for command
            with Vertical(id='top-right'):
                yield Placeholder('Search')

            # display command
            with Vertical(id='bottom'):
                yield Placeholder('Preview')

    def on_mount(self) -> None:
        # header values
        self.title = 'Hackros'
        self.sub_title = 'Template Injection Who?'

class LabeledInput(Widget):
    """ Label that accepts IP inputs """

    # TODO figure out how to center the label
    # and restrict masked input size
    DEFAULT_CSS = """
    LabeledInput {
        width: 1fr;
        height: auto;
    }
    #ip-label {
        align: center middle;
        border: black;
    }
    #ip-input {
        width: 1fr;
    }
    #ip-grid {
        layout: grid; /* horizontal;*/
        grid-size: 2; /* num cols */
        grid-columns: 1fr 3fr;
        grid-rows: 2fr;
    }
    """

    def __init__(self, name: str, id: str) -> None:
        self.label_name = name
        super().__init__(id=id)

    @on(Input.Submitted)
    def submit(self, event: Input.Submitted) -> None:
        ip = event.input.value
        self.post_message(HackroMessage(ip, super().id))

    def compose(self) -> ComposeResult:
        with Horizontal(id='ip-grid'):
            yield Static(self.label_name, id='ip-label')
            # yield MaskedInput(template='900.900.900.900')
            yield Input(id='ip-input')
        # yield Label(f'Current {self.label_name} None', id='output_label')

if __name__ == '__main__':
    app = HackrosApp()
    app.run()
