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

    def test_buttmeon(self, status=u'Butt enabled, use /buttmeoff to disable it'):
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
        self.plugin.cron_go('instagram.butt', '')
        self.assertEqual(len(self.bot._sent_messages), 0)
        self.test_buttmeon()
        self.plugin.cron_go('instagram.butt', 'test cron')
        self.assertReplied(self.bot, 'test cron')

    def test_butt_cron_blocked(self):
        self.test_buttmeon()  # enable buttme
        self.bot.return_blocked_error = True  # block bot
        self.plugin.cron_go('instagram.butt', 'test cron')
        self.assertReplied(self.bot, 'test cron')
        self.test_buttme()  # check buttme was disabled
