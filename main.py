from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
import os

class PassExtension(Extension):

    def __init__(self):
        super(PassExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []
    	pipe = os.popen("find ~/.password-store/ | sed '/gpg$/!d;s/.*.password-store\///;s/.gpg$//'")
    	output = pipe.read()
        myList = event.query.split(" ")
        custom_command = extension.preferences['custom_command']
        custom_command_delay = extension.preferences['custom_command_delay']

        if not myList[1]:
            for line in output.splitlines():
                sleep = "sleep 0" if not custom_command_delay else "sleep " + custom_command_delay
                command = "pass show -c %s" % line
                command = command if not custom_command else " && ".join([custom_command, command, sleep, custom_command])
                items.append(ExtensionResultItem(icon='images/key.png',
                                                name='%s' % line,
                                                description='Copy %s to clipboard' % line,
                                                on_enter=RunScriptAction(command, None)))
        else:
            myQuery = [item.lower() for item in myList[1:]]
            for line in output.splitlines():
                sleep = "sleep 0" if not custom_command_delay else "sleep " + custom_command_delay
                command = "pass show -c %s" % line
                command = command if not custom_command else " && ".join([custom_command, command, sleep, custom_command])
                if all(word in line.lower() for word in myQuery):
                    items.append(ExtensionResultItem(icon='images/key.png',
                                                name='%s' % line,
                                                description='Copy %s to clipboard' % line,
                                                on_enter=RunScriptAction(command, None)))

        return RenderResultListAction(items[:10])

if __name__ == '__main__':
    PassExtension().run()
