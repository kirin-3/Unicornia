"""Module to collect action data

Provide a simple interface into action properties

Roleplay action commands are defined as individual YAML files in "actions" subfolder
"""

import logging
from pathlib import Path
import yaml

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Union

FILEPATH = Path(__file__).parent / "actions"
FILETYPE = "yml"


@dataclass
class Denial:
    """Represents the denial properties for an action.

    Attributes:
        roles (List[int]): List of role IDs that would prevent the action from being
        completed successfully.
        message (str): The message displayed when the action is denied.
        Ex: "{invoker_member} can't ___ {target_member} in their current state."
    """

    message: str
    roles: Union[List[str], str] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.roles, str):
            self.roles = [self.roles]


@dataclass
class Consent:
    """Represents the consent properties for an action.

    Attributes:
        roles (bool): Indicates if roles require consent (default is True).
        active (str): The message displayed when asking for active consent.
            Ex: "{target_member}, {invoker_member} wants to ___ you."
        passive (str): The message displayed when asking for passive consent.
            Ex: "{invoker_member}, {target_member} wants you to ___ them."
        owner_active (str): The message displayed when asking for consent from an owner(s).
            Ex: "{owner}, {invoker_member} wants to ___ {target_member}."
        owner_passive (str): The message displayed when asking for consent from an owner(s).
            Ex: "{owner}, {invoker_member} wants {target_member} to ___ them."
    """

    active: str
    passive: str
    owner_active: str
    owner_passive: str


@dataclass
class Action:
    """Represents an action in roleplay.

    Attributes:
        name (str): The name of the action.
        help (str): The docstring added to each action command method. Displayed in 'help' messages generated by the bot.
        description (str): The Embed description, describing the roleplay action in present tense. Use {invoker_member} and {target_member} tags.
        aliases (Optional[List[str]]): Aliases for the command name.
        credits (Optional[List[str]]): Optional credits text included in the Embed footer to acknowledge members who came up with the idea.
        spoiler (Optional[bool]): Use for lewd images. This will spoiler the image in a message instead of displaying it in an Embed.
        images (Optional[list]): URL for a gif(s) that represents the action.
        consent (Optional[Consent]): If this is included, the action requires consent. Under this property, messages to ask for consent can be defined.
        denial (Optional[Denial]): If this is included, roles can be defined that would prevent the action from being completed successfully.
    """

    name: str
    description: str
    help: str
    aliases: Union[List[str], str] = field(default_factory=list)
    credits: Optional[List[str]] = None
    spoiler: Optional[bool] = False
    images: Union[List[str], str] = field(default_factory=list)
    consent: Optional[Consent] = None
    denial: Optional[Denial] = None

    def __post_init__(self):
        if self.description is None:
            self.description = (
                "{invoker_member} is " + f"{self.name}ing" + " {target_member}."
            )
        if self.help is None:
            self.help = f"{self.name}s a member."
        if isinstance(self.aliases, str):
            self.aliases = [self.aliases]
        if isinstance(self.images, str):
            self.images = [self.images]
        if isinstance(self.consent, dict):
            try:
                self.consent = Consent(**self.consent)
            except TypeError:
                print(f"""Bad "Consent" data: {self.consent}""")
        if isinstance(self.denial, dict):
            try:
                self.denial = Denial(**self.denial)
            except TypeError:
                print(f"""Bad "Denial" data: {self.consent}""")


class ActionManager:
    DATA_PATH = Path(__file__).parent / "actions"

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        self.actions: List[Action] = []

        self.load_all()

    def __str__(self):
        actions = [str(action) for action in self.actions]
        actions = "\n\t".join(actions)
        return f"ActionManager: {actions}"

    def load(self, action_name: str, file_path: Union[str | Path] = None) -> Action:
        if not file_path:
            file_path = Path(self.DATA_PATH) / f"{action_name}.yml"

        with open(file_path, "r") as file:
            try:
                data = yaml.safe_load(file)
            except:
                self.logger.error(f"Error trying to parse {file_path}!")
                return None
            action = Action(name=action_name, **data)
            return action

    def load_all(self):
        yaml_files = (
            file
            for pattern in ("*.yaml", "*.yml")
            for file in self.DATA_PATH.glob(pattern)
        )

        for file_path in yaml_files:
            action_name = file_path.stem
            action = self.load(action_name, file_path=file_path)

            if not action:
                continue

            self.actions.append(action)
            # add property as pointer to the action
            setattr(self, action_name, action)

    def get(self, action_name):
        for action in self.actions:
            if action.name == action_name:
                return action

        self.logger.warning(f'Unable to find action "{action_name}"!')
        return None

    def list(self):
        action_names = [action.name for action in self.actions]
        action_names.sort()
        return action_names


# Test
if __name__ == "__main__":
    from pprint import pprint

    manager = ActionManager()
    names = manager.list()

    print("Actions:")
    pprint(names, indent=4)

    action_name = "suck"
    action = manager.get(action_name)

    if action:
        print(f"Name: {action.name}")
        print(f"Help: {action.help}")
        print(f"Description: {action.description}")
        print(f"Aliases: {action.aliases}")
        print(f"Images:")
        pprint(action.images, indent=4)

        # Test for consent
        if action.consent:
            print(f'Consent Message (active): "{action.consent.active}"')
            print(f'Consent Message (passive): "{action.consent.passive}"')
            print(f'Owner Consent Message (active): "{action.consent.owner_active}"')
            print(f'Owner Consent Message (passive) "{action.consent.owner_passive}"')

        # Test for denial
        if action.denial:
            print("Denial Roles:")
            pprint(action.denial.roles, indent=4)
            print(f"Denial Message:\n\t{action.denial.message}")
    else:
        print(f"Action '{action_name}' not found!")
