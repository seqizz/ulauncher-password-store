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
        if len(myList) == 1:
            for line in output.splitlines():
                items.append(ExtensionResultItem(icon='images/key.png',
                                                name='%s' % line,
                                                description='Copy %s to clipboard' % line,
                                                on_enter=RunScriptAction("pass show -c %s" % line, None)))

            return RenderResultListAction(items)
        else:
            myQuery = myList[1].lower()
            for line in output.splitlines():
                if myQuery in line.lower():
                    items.append(ExtensionResultItem(icon='images/key.png',
                                                name='%s' % line,
                                                description='Copy %s to clipboard' % line,
                                                on_enter=RunScriptAction("pass show -c %s" % line, None)))

            return RenderResultListAction(items)

if __name__ == '__main__':
    PassExtension().run()
