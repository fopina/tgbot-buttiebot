# coding=utf-8
from tgbot.pluginbase import TGPluginBase, TGCommandBase
from tgbot.tgbot import ChatAction, InputFile, InputFileInfo, Error, ForceReply
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
            TGCommandBase('buttgmt', self.buttgmt, 'Set your timezone'),
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
                ('buttsnorkeler', u'^.?Snorkeled'),
                # ('buttbuilding', ' '),  # crappy one...
            ))
            r = requests.get('https://instagram.com/%s/' % ig)
            m = re.findall('<script type="text\/javascript">window._sharedData = (.*?);<\/script>', r.content)
            s = json.loads(m[0])
            try:
                pics = [x for x in s['entry_data']['ProfilePage'][0]['user']['media']['nodes'] if re.match(keyword_filter, x['caption'])]
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

    def buttgmt(self, message, text):
        self.bot.send_chat_action(message.chat.id, ChatAction.TEXT)
        if not text:
            m = self.bot.send_message(
                message.chat.id,
                '''\
What's your GMT offset?
Example, if you are in Beijing (China), the timezone is GMT+8, so you answer:
*8*
If you are in Boston (USA), it is GMT-5, so you answer:
*-5*
Apologies to India, Iran and some other places, but offsets are integers at the moment, so half-hour deviations are not supported...''',
                reply_to_message_id=message.message_id,
                reply_markup=ForceReply.create(selective=True),
                parse_mode='Markdown'
            ).wait()
            self.need_reply(self.buttgmt, message, out_message=m, selective=True)
            return

        try:
            offset = int(text)
        except:
            offset = -999

        if offset < -12 or offset > 12:
            res = 'Invalid offset value. It should be a number between -12 and 12 (no half-hour offsets at the moment, apologies to India, Iran, etc)'
        else:
            res = 'Timezone set to GMT'
            if offset >= 0:
                res += '+'
            res += str(offset)
            self.save_data(message.chat.id, key2='timezone', obj=offset)

        self.bot.send_message(message.chat.id, res, parse_mode='Markdown')

    def buttme(self, message, text):
        a = self.read_data(message.chat.id)
        try:
            offset = int(self.read_data(message.chat.id, 'timezone'))
        except:
            offset = 0

        tz = 'GMT'
        if offset >= 0:
            tz += '+'
        tz += str(offset)

        if a is True:
            msg = '''\
Butt enabled, use /buttmeoff to disable it.
Your timezone is set to *%s*, use /buttgmt to change it.''' % tz
        else:
            msg = 'Butt disabled, use /buttmeon to enable it'

        self.bot.send_message(message.chat.id, msg, parse_mode='Markdown')

    def buttmeon(self, message, text):
        self.save_data(message.chat.id, obj=True)
        try:
            offset = int(self.read_data(message.chat.id, 'timezone'))
        except:
            offset = 0

        tz = 'GMT'
        if offset >= 0:
            tz += '+'
        tz += str(offset)

        self.bot.send_message(message.chat.id, '''\
Butt enabled, use /buttmeoff to disable it.
Your timezone is set to *%s*, use /buttgmt to change it.''' % tz, parse_mode='Markdown')

    def buttmeoff(self, message, text):
        self.save_data(message.chat.id, obj=False)
        self.bot.send_message(message.chat.id, 'Butt disabled, use /buttmeon to enable it')

    def cron_go(self, action, *args):
        if action == 'instagram.butt':
            return self.cron_butt()
        elif action == 'instagram.broadcast':
            return self.cron_broadcast(*args)

    def cron_butt(self):
        import time

        hour = time.gmtime().tm_hour
        for chat in self.iter_data_keys():
            if chat == 'cache':
                continue
            if self.read_data(chat):
                try:
                    offset = int(self.read_data(chat, 'timezone'))
                    if not offset:
                        offset = 0
                except:
                    offset = 0

                lhour = (hour + offset) % 24

                if lhour == 9:
                    msg = 'Good morning!'
                elif lhour == 13:
                    msg = 'Bon appetit!'
                elif lhour == 18:
                    msg = 'Time to relax...'
                else:
                    continue

                print "Sending butt to %s" % chat
                time_start = time.time()
                r = self._butt(chat, msg)
                if isinstance(r, Error):
                    if r.error_code == 403:
                        print '%s blocked bot' % chat
                        self.save_data(chat, obj=False)
                    else:
                        print 'Error for', chat, ': ', r  # pragma: no cover
                time_taken = time.time() - time_start
                if time_taken < 0.5:  # pragma: no cover
                    time.sleep(0.5 - time_taken)

    def cron_broadcast(self, message):
        '''
        Broadcast a message to all /buttme subscribers
        '''
        import time

        if not message:
            import sys
            message = sys.stdin.read()

        for chat in self.iter_data_keys():
            if chat == 'cache':
                continue
            if self.read_data(chat):
                print "Sending message to %s" % chat
                time_start = time.time()
                r = self.bot.send_message(chat, message, parse_mode='Markdown').wait()
                if isinstance(r, Error):
                    print 'Error for', chat, ': ', r  # pragma: no cover
                time_taken = time.time() - time_start
                if time_taken < 0.5:  # pragma: no cover
                    time.sleep(0.5 - time_taken)
