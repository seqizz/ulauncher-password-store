from glib import markup_escape_text
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from os import walk, path, access, environ, pathsep, X_OK
from subprocess import check_output, CalledProcessError

# TODO: Also utilize the python-pwgen module
# We fall back to pwgen command if the module is not there
# try:
#    import pwgen
# except ImportError:
#    pwgen_module = False


def is_exist(program):
    def is_exe(fpath):
        return path.isfile(fpath) and access(fpath, X_OK)

    fpath, fname = path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for mypath in environ["PATH"].split(pathsep):
            exe_file = path.join(mypath, program)
            if is_exe(exe_file):
                return exe_file

    return None


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
                    if root == top:
                        t += [name]
                    else:
                        t += ["{}/{}".format(path.relpath(root, top), name)]
        return sorted(t)

    def on_event(self, event, extension):
        items = []
        myList = event.query.split(" ")
        password_store_path = extension.preferences['password_store_path']
        if "~" in password_store_path:
            password_store_path = path.expanduser(password_store_path)
        custom_command = extension.preferences['custom_command']
        custom_command_delay = extension.preferences['custom_command_delay']
        enable_tail = extension.preferences['enable_tail']
        gen_shortcut = extension.preferences['gen_shortcut']
        use_pwgen = extension.preferences['use_pwgen']
        pass_list = self.list_gpg(password_store_path)

        if not myList[1]:
            for line in pass_list:
                if not custom_command_delay:
                    custom_command_delay = 0
                sleep = "sleep " + str(custom_command_delay)
                command = "pass show -c {}".format(line)
                if custom_command:
                    command = " && ".join(
                        [custom_command, command, sleep, custom_command]
                    )
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
            if myList[1] == gen_shortcut:
                passwords = ''
                if use_pwgen and not is_exist(program='pwgen'):
                    items.append(
                        ExtensionResultItem(
                            icon='images/key.png',
                            name='Couldn\'t find pwgen',
                            description='Please install it and make sure it\'s in PATH'
                            )
                        )
                    return

                if use_pwgen and len(myList) == 2:
                    command = 'pwgen -1 -c -n -y 16 8'
                    output = check_output(command.split(' '))
                    passwords = output.splitlines()

                if use_pwgen and len(myList) > 2:
                    if not str(myList[2]).isdigit():
                        items.append(
                            ExtensionResultItem(
                                    icon='images/key.png',
                                    name='Please enter a password length',
                                    description='By default it\'s 16',
                                    highlightable=False
                                )
                            )
                    else:
                        command = 'pwgen -1 -c -n -y {} 8'.format(str(myList[2]))
                        output = check_output(command.split(' '))
                        passwords = output.splitlines()

                if passwords:
                    for line in passwords:
                        if not custom_command_delay:
                            custom_command_delay = 0
                        sleep = "sleep " + str(custom_command_delay)
                        command = "pass show -c {}".format(line)
                        if custom_command:
                            command = " && ".join(
                                [custom_command, command, sleep, custom_command]
                            )
                        items.append(
                            ExtensionResultItem(
                                icon='images/key.png',
                                name=markup_escape_text(line),
                                description='Copy {} to clipboard'.format(line),
                                on_enter=RunScriptAction(command, None)
                            )
                        )
                # We are not returning here, in case we have similar password
                # to the gen_shortcut

            for line in pass_list:
                if not custom_command_delay:
                    custom_command_delay = 0
                sleep = "sleep " + str(custom_command_delay)
                command = "pass show -c %s" % line
                if custom_command:
                    command = " && ".join(
                        [custom_command, command, sleep, custom_command]
                    )
                if all(word in line.lower() for word in myQuery if word != "tail"):
                    try:
                        if enable_tail and myQuery[-1] == "tail":
                            extra = "\n" + check_output(["pass", "tail", line]).strip()
                        else:
                            extra = ''
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
                    # `pass tail` command requires time to process.
                    # It's best to break it after first result.
                    if extra:
                        break

        return RenderResultListAction(items[:10])

if __name__ == '__main__':
    PassExtension().run()
