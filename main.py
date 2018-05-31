from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from os import walk, path
from subprocess import check_output, CalledProcessError

class PassExtension(Extension):

    def __init__(self):
        super(PassExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def list_gpg(self, top):
        t = []
        for root, dirs, files in walk(top):
            for f in files:
                name, ext = path.splitext(f)
                if ext == ".gpg":
                    t += [name if root == top else "{}/{}".format(path.relpath(root, top), name)]
        return sorted(t)

    def on_event(self, event, extension):
        items = []
        myList = event.query.split(" ")
        password_store_path = extension.preferences['password_store_path']
        password_store_path = path.expanduser(password_store_path) if "~" in password_store_path else password_store_path
        custom_command = extension.preferences['custom_command']
        custom_command_delay = extension.preferences['custom_command_delay']
        enable_tail = extension.preferences['enable_tail']
        pass_list = self.list_gpg(password_store_path)

        if not myList[1]:
            for line in pass_list:
                sleep = "sleep 0" if not custom_command_delay else "sleep " + custom_command_delay
                command = "pass show -c %s" % line
                command = command if not custom_command else " && ".join([custom_command, command, sleep, custom_command])
                items.append(
                    ExtensionResultItem(
                        icon='images/key.png',
                        name='%s' % line,
                        description='Copy %s to clipboard' % line,
                        on_enter=RunScriptAction(command, None)
                    )
                )
        else:
            myQuery = [item.lower() for item in myList[1:]]
            for line in pass_list:
                sleep = "sleep 0" if not custom_command_delay else "sleep " + custom_command_delay
                command = "pass show -c %s" % line
                command = command if not custom_command else " && ".join([custom_command, command, sleep, custom_command])
                if all(word in line.lower() for word in myQuery if word != "tail"):
                    try:
                        extra = "\n" + check_output(["pass", "tail", line]).strip() \
                                if enable_tail and myQuery[-1] == "tail" else ''
                    except CalledProcessError:
                        items.append(
                            ExtensionResultItem(
                                icon='images/key.png',
                                name='Pass tail extension is not installed',
                                description='Press Enter to go to the extension\'s website',
                                on_enter=OpenUrlAction('https://git.io/vpSgV')
                            )
                        )
                        break

                    items.append(
                        ExtensionResultItem(
                            icon='images/key.png',
                            name='%s' % line,
                            description='Copy %s to clipboard%s' % (line, extra),
                            on_enter=RunScriptAction(command, None)
                        )
                    )
                    # `pass tail` command requires time to process. It's best to break it after first result.
                    if extra:
                        break

        return RenderResultListAction(items[:10])

if __name__ == '__main__':
    PassExtension().run()
