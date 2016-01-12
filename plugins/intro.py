# coding=utf-8
from tgbot.pluginbase import TGPluginBase, TGCommandBase


class IntroPlugin(TGPluginBase):
    def list_commands(self):
        return (
            TGCommandBase('start', self.start, 'Introduction', printable=False),
        )

    def start(self, message, text):
        self.bot.send_message(
            message.chat.id,
            '''\
If you'd like to be cheered at the right time of the day, try /buttme

Anytime you feel like, you can request a /butt

Do not forget to rate me!
https://telegram.me/storebot?start=buttiebot
            ''',
            parse_mode='Markdown'
        )
