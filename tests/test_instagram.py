# coding=utf-8
from tgbot import plugintest
from tgbot.botapi import Update, Message, Error
from plugins.instagram import InstagramPlugin

from requests.packages import urllib3
urllib3.disable_warnings()


class FakePhotoTelegramBot(plugintest.FakeTelegramBot):
    # TODO - improve this and it to tgbotplug
    def __init__(self, *args, **kwargs):
        plugintest.FakeTelegramBot.__init__(self, *args, **kwargs)
        self.return_blocked_error = False

    def send_photo(self, chat_id, photo, caption=None, reply_to_message_id=None, reply_markup=None, **kwargs):
        self._sent_messages.append(([chat_id, caption], kwargs))
        self._current_message_id += 1
        if self.return_blocked_error:
            return FakePhotoTelegramBot.FakeRPCRequest(
                Error.from_result({'ok': False, 'error_code': 403})
            )
        else:
            return FakePhotoTelegramBot.FakeRPCRequest(Message.from_result({
                'message_id': self._current_message_id,
                'chat': {
                    'id': chat_id,
                }
            }))


class InstagramPluginTest(plugintest.PluginTestCase):
    def setUp(self):
        self.plugin = InstagramPlugin()
        self.bot = FakePhotoTelegramBot('', plugins=[self.plugin])
        self.received_id = 1

    def receive_message(self, text, sender=None, chat=None):
        if sender is None:
            sender = {
                'id': 1,
                'first_name': 'John',
                'last_name': 'Doe',
            }

        if chat is None:
            chat = sender

        self.bot.process_update(
            Update.from_dict({
                'update_id': self.received_id,
                'message': {
                    'message_id': self.received_id,
                    'text': text,
                    'chat': chat,
                    'from': sender,
                }
            })
        )

        self.received_id += 1

    def test_buttme(self, status=u'Butt disabled, use /buttmeon to enable it'):
        self.receive_message('/buttme')
        self.assertReplied(self.bot, status)

    def test_buttmeon(self, status=u'''\
Butt enabled, use /buttmeoff to disable it.
Your timezone is set to *GMT+0*, use /buttgmt to change it.'''):
        self.test_buttme()
        self.receive_message('/buttmeon')
        self.assertReplied(self.bot, status)
        self.test_buttme(status=status)

    def test_buttmeoff(self, status=u'Butt disabled, use /buttmeon to enable it'):
        self.test_buttmeon()
        self.receive_message('/buttmeoff')
        self.assertReplied(self.bot, status)
        self.test_buttme()

    def test_butt(self):
        self.receive_message('/butt')
        self.assertIn('Snorkeled', self.last_reply(self.bot))
        self.receive_message('/butt')
        self.assertIn('Snorkeled', self.last_reply(self.bot))

    def test_butt_repeat(self):
        import mock

        def fget(*args, **kwargs):
            r = type('Test', (object,), {})
            r.content = '''
            <script type="text/javascript">window._sharedData = {"entry_data":{"ProfilePage":[{"user": {"media": {"nodes":[{"caption": "Snorkeled", "id": "123", "likes": {"count": 1}, "display_src": "http://i1079.photobucket.com/albums/w514/skmobi/skmobi/site/logo.png"}]}}}]}};</script>
            '''
            return r

        with mock.patch('requests.get', fget):
            self.receive_message('/butt')
            self.assertIn('Snorkeled', self.last_reply(self.bot))
            self.receive_message('/butt')
            self.assertReplied(self.bot, 'Sorry, no new butts found right now...')

    def test_butt_no_pics(self):
        import mock

        def fget(*args, **kwargs):
            r = type('Test', (object,), {})
            r.content = '''
            <script type="text/javascript">window._sharedData = {};</script>
            '''
            return r

        with mock.patch('requests.get', fget):
            self.receive_message('/butt')
            self.assertReplied(self.bot, 'Sorry, no new butts found right now...')

    def test_butt_cron(self):
        import mock
        import time
        import requests

        rget = requests.get

        # no need to actually download the pictures here...
        def nopicget(*args, **kwargs):
            if 'cdninstagram.com' in args[0]:
                r = type('Test', (object,), {})
                r.content = ''
                return r
            return rget(*args, **kwargs)

        with mock.patch('requests.get', nopicget):
            with mock.patch(
                'time.gmtime',
                return_value=time.struct_time((2016, 1, 18, 9, 50, 36, 0, 18, 0))
            ):
                self.plugin.cron_go('instagram.butt')
                self.assertEqual(len(self.bot._sent_messages), 0)
                self.test_buttmeon()
                self.plugin.cron_go('instagram.butt')
                self.assertReplied(self.bot, 'Good morning!')

            with mock.patch(
                'time.gmtime',
                return_value=time.struct_time((2016, 1, 18, 13, 50, 36, 0, 18, 0))
            ):
                self.plugin.cron_go('instagram.butt')
                self.assertReplied(self.bot, 'Bon appetit!')

            with mock.patch(
                'time.gmtime',
                return_value=time.struct_time((2016, 1, 18, 18, 50, 36, 0, 18, 0))
            ):
                self.plugin.cron_go('instagram.butt')
                self.assertReplied(self.bot, 'Time to relax...')

            with mock.patch(
                'time.gmtime',
                return_value=time.struct_time((2016, 1, 18, 20, 50, 36, 0, 18, 0))
            ):
                self.bot._sent_messages = []  # clear messages
                self.plugin.cron_go('instagram.butt')
                self.assertRaisesRegexp(AssertionError, 'No replies', self.last_reply, self.bot)

    def test_butt_cron_blocked(self):
        self.test_buttmeon()  # enable buttme
        self.bot.return_blocked_error = True  # block bot

        import mock
        import time

        with mock.patch(
            'time.gmtime',
            return_value=time.struct_time((2016, 1, 18, 13, 50, 36, 0, 18, 0))
        ):
            self.plugin.cron_go('instagram.butt')
            self.assertReplied(self.bot, 'Bon appetit!')  # some message was still sent, doesn't really matter
            self.test_buttme()  # check buttme was disabled

    def test_buttgmt(self):
        self.receive_message('/buttgmt +3')
        self.assertReplied(self.bot, 'Timezone set to GMT+3')
        self.test_buttmeon(status=u'''\
Butt enabled, use /buttmeoff to disable it.
Your timezone is set to *GMT+3*, use /buttgmt to change it.''')

        import mock
        import time

        with mock.patch(
            'time.gmtime',
            return_value=time.struct_time((2016, 1, 18, 9, 50, 36, 0, 18, 0))
        ):
            self.bot._sent_messages = []  # clear messages
            self.plugin.cron_go('instagram.butt')
            self.assertRaisesRegexp(AssertionError, 'No replies', self.last_reply, self.bot)

        with mock.patch(
            'time.gmtime',
            return_value=time.struct_time((2016, 1, 18, 6, 50, 36, 0, 18, 0))
        ):
            self.plugin.cron_go('instagram.butt')
            self.assertReplied(self.bot, 'Good morning!')

        self.receive_message('/buttgmt -5')
        self.assertReplied(self.bot, 'Timezone set to GMT-5')

        with mock.patch(
            'time.gmtime',
            return_value=time.struct_time((2016, 1, 18, 18, 50, 36, 0, 18, 0))
        ):
            self.plugin.cron_go('instagram.butt')
            self.assertReplied(self.bot, 'Bon appetit!')

    def test_buttgmt_validation(self, error_msg='Invalid offset value. It should be a number between -12 and 12'):
        self.receive_message('/buttgmt')
        self.receive_message('3')
        self.assertReplied(self.bot, 'Timezone set to GMT+3')
        self.receive_message('/buttgmt a')
        self.assertReplied(self.bot, error_msg)
        self.receive_message('/buttgmt -5')
        self.assertReplied(self.bot, 'Timezone set to GMT-5')
        self.receive_message('/buttgmt -11.5')
        self.assertReplied(self.bot, error_msg)
        self.receive_message('/buttgmt 0')
        self.assertReplied(self.bot, 'Timezone set to GMT+0')
        self.receive_message('/buttgmt 14')
        self.assertReplied(self.bot, error_msg)
