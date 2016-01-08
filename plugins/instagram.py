# coding=utf-8
from tgbot.pluginbase import TGPluginBase, TGCommandBase
from tgbot.tgbot import ChatAction, InputFile, InputFileInfo
from random import choice
import requests
import re
import json
from cStringIO import StringIO
import mimetypes


class InstagramPlugin(TGPluginBase):
    def list_commands(self):
        return (
            TGCommandBase('butt', self.butt, 'Random butt to cheer your day'),
            TGCommandBase('buttme', self.buttme, 'Get a butt at the right time of the day'),
            TGCommandBase('buttmeon', self.buttmeon, 'Enable /buttme', printable=False),
            TGCommandBase('buttmeoff', self.buttmeoff, 'Disable /buttme', printable=False),
        )

    def butt(self, message, text):
        self._butt(message.chat.id, text)

    def _butt(self, chat_id, text):
        self.bot.send_chat_action(chat_id, ChatAction.TEXT)
        for i in xrange(3):
            ig = choice((
                'buttsnorkeler',
                # 'buttbuilding',  # crappy one...
            ))
            r = requests.get('https://instagram.com/%s/' % ig)
            m = re.findall('<script type="text\/javascript">window._sharedData = (.*?);</script>', r.content)
            s = json.loads(m[0])
            last_pics = self.read_data(chat_id, key2='last_' + ig)
            try:
                pics = s['entry_data']['ProfilePage'][0]['user']['media']['nodes']
                break
            except KeyError:
                pass
            from time import sleep
            sleep(1)
        if last_pics is None:
            last_pics = []
        else:
            pics = [x for x in pics if x['id'] not in last_pics]
        pic = choice(pics)

        last_pics.append(pic['id'])
        if len(last_pics) > 10:
            del last_pics[0]
        self.save_data(chat_id, key2='last_' + ig, obj=last_pics)

        fp = StringIO(requests.get(pic['display_src']).content)
        file_info = InputFileInfo(pic['display_src'].split('/')[-1], fp, mimetypes.guess_type(pic['display_src'])[0])

        if not text:
            text = '%s (%d likes)' % (pic['caption'], pic['likes']['count'])

        self.bot.send_photo(chat_id=chat_id, caption=text, photo=InputFile('photo', file_info))

    def buttme(self, message, text):
        a = self.read_data(message.chat.id)

        if a is True:
            msg = 'Butt enabled, use /buttmeoff to disable it'
        else:
            msg = 'Butt disabled, use /buttmeon to enable it'

        self.bot.send_message(message.chat.id, msg)

    def buttmeon(self, message, text):
        self.save_data(message.chat.id, obj=True)
        self.bot.send_message(message.chat.id, 'Butt enabled, use /buttmeoff to disable it')

    def buttmeoff(self, message, text):
        self.save_data(message.chat.id, obj=False)
        self.bot.send_message(message.chat.id, 'Butt disabled, use /buttmeon to enable it')

    def cron_go(self, action, param):
        if action == 'instagram.butt':
            for chat in self.iter_data_keys():
                if self.read_data(chat):
                    print "Sending butt to %s" % chat
                    self._butt(chat, param)
