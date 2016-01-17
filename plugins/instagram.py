# coding=utf-8
from tgbot.pluginbase import TGPluginBase, TGCommandBase
from tgbot.tgbot import ChatAction, InputFile, InputFileInfo, Error
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
        self.bot.send_chat_action(chat_id, ChatAction.PHOTO)

        pics = []
        for i in xrange(3):
            ig, keyword_filter = choice((
                ('buttsnorkeler', 'Snorkeled'),
                # ('buttbuilding', ' '),  # crappy one...
            ))
            r = requests.get('https://instagram.com/%s/' % ig)
            m = re.findall('<script type="text\/javascript">window._sharedData = (.*?);<\/script>', r.content)
            s = json.loads(m[0])
            try:
                pics = [x for x in s['entry_data']['ProfilePage'][0]['user']['media']['nodes'] if keyword_filter in x['caption']]
                break
            except KeyError:
                pass
            from time import sleep
            sleep(1)

        pics = [x for x in pics if not self.read_data(chat_id, x['id'])]
        if not pics:
            return self.bot.send_message(chat_id, 'Sorry, no new butts found right now...').wait()
        pic = choice(pics)

        self.save_data(chat_id, key2=pic['id'], obj=True)

        if not text:
            text = '%s (%d likes)' % (pic['caption'], pic['likes']['count'])

        photo = self.read_data('cache', key2=pic['id'])

        if photo:
            r = self.bot.send_photo(chat_id=chat_id, caption=text, photo=photo.encode('utf-8')).wait()
            if not isinstance(r, Error):
                return r

        fp = StringIO(requests.get(pic['display_src']).content)
        file_info = InputFileInfo(pic['display_src'].split('/')[-1], fp, mimetypes.guess_type(pic['display_src'])[0])
        r = self.bot.send_photo(chat_id=chat_id, caption=text, photo=InputFile('photo', file_info)).wait()

        if isinstance(r, Error):
            return r
        if r.photo:
            self.save_data('cache', key2=pic['id'], obj=r.photo[0].file_id)
        return r

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
            from time import sleep

            for chat in self.iter_data_keys():
                if chat == 'cache':
                    continue
                if self.read_data(chat):
                    print "Sending butt to %s" % chat
                    r = self._butt(chat, param)
                    if isinstance(r, Error):
                        if r.error_code == 403:
                            print '%s blocked bot' % chat
                            self.save_data(chat, obj=False)
                        else:
                            print 'Error for', chat, ': ', r  # pragma: no cover
                    sleep(0.5)
