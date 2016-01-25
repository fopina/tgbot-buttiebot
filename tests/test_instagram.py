# coding=utf-8
from tgbot import plugintest
from plugins.instagram import InstagramPlugin

from requests.packages import urllib3
urllib3.disable_warnings()


class PluginTest(plugintest.PluginTestCase):
    def setUp(self):
        self.plugin = InstagramPlugin()
        self.bot = self.fake_bot('', plugins=[self.plugin])

    def test_buttme(self, status=u'Butt disabled, use /buttmeon to enable it'):
        self.receive_message('/buttme')
        self.assertReplied(status)

    def test_buttmeon(self, status=u'''\
Butt enabled, use /buttmeoff to disable it.
Your timezone is set to *GMT+0*, use /buttgmt to change it.'''):
        self.test_buttme()
        self.receive_message('/buttmeon')
        self.assertReplied(status)
        self.test_buttme(status=status)

    def test_buttmeoff(self, status=u'Butt disabled, use /buttmeon to enable it'):
        self.test_buttmeon()
        self.receive_message('/buttmeoff')
        self.assertReplied(status)
        self.test_buttme()

    def test_butt(self):
        self.receive_message('/butt')
        self.assertIn('Snorkeled', self.pop_reply()[1]['caption'])
        self.receive_message('/butt')
        self.assertIn('Snorkeled', self.pop_reply()[1]['caption'])

    def test_butt_snorkeled(self):
        import mock

        def fget(*args, **kwargs):
            r = type('Test', (object,), {})
            r.content = '''
            <script type="text/javascript">window._sharedData = {"entry_data":{"ProfilePage":[{"user": {"media": {"nodes":[{"caption": "Snorkeled", "id": "123", "likes": {"count": 1}, "display_src": "http://i1079.photobucket.com/albums/w514/skmobi/skmobi/site/logo.png"}]}}}]}};</script>
            '''
            return r

        with mock.patch('requests.get', fget):
            self.receive_message('/butt')
            self.assertIn('Snorkeled', self.pop_reply()[1]['caption'])

    def test_butt_snorkeled_not(self):
        import mock

        def fget(*args, **kwargs):
            r = type('Test', (object,), {})
            r.content = '''
            <script type="text/javascript">window._sharedData = {"entry_data":{"ProfilePage":[{"user": {"media": {"nodes":[{"caption": "Eh #Snorkeled", "id": "123", "likes": {"count": 1}, "display_src": "http://i1079.photobucket.com/albums/w514/skmobi/skmobi/site/logo.png"}]}}}]}};</script>
            '''
            return r

        with mock.patch('requests.get', fget):
            self.receive_message('/butt')
            self.assertReplied('Sorry, no new butts found right now...')

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
            self.assertIn('Snorkeled', self.pop_reply()[1]['caption'])
            self.receive_message('/butt')
            self.assertReplied('Sorry, no new butts found right now...')

    def test_butt_cache(self):
        import mock

        def fget(*args, **kwargs):
            r = type('Test', (object,), {})
            r.content = '''
            <script type="text/javascript">window._sharedData = {"entry_data":{"ProfilePage":[{"user": {"media": {"nodes":[{"caption": "Snorkeled", "id": "123", "likes": {"count": 1}, "display_src": "http://i1079.photobucket.com/albums/w514/skmobi/skmobi/site/logo.png"}]}}}]}};</script>
            '''
            return r

        # insert cache entry
        self.plugin.save_data('cache', key2='123', obj='whatever')

        with mock.patch('requests.get', fget):
            self.push_fake_result({
                'message_id': None,
                'chat': {'id': 1},
                'photo': [{'file_id': '123_AB-C'}]
            })
            self.push_fake_result(True)
            self.receive_message('/butt')
            self.assertIn('Snorkeled', self.pop_reply()[1]['caption'])

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
            self.assertReplied('Sorry, no new butts found right now...')

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
                self.assertNoReplies()
                self.test_buttmeon()
                self.plugin.cron_go('instagram.butt')
                self.assertEqual(self.pop_reply()[1]['caption'], 'Good morning!')

            with mock.patch(
                'time.gmtime',
                return_value=time.struct_time((2016, 1, 18, 13, 50, 36, 0, 18, 0))
            ):
                self.plugin.cron_go('instagram.butt')
                self.assertEqual(self.pop_reply()[1]['caption'], 'Bon appetit!')

            with mock.patch(
                'time.gmtime',
                return_value=time.struct_time((2016, 1, 18, 18, 50, 36, 0, 18, 0))
            ):
                self.plugin.cron_go('instagram.butt')
                self.assertEqual(self.pop_reply()[1]['caption'], 'Time to relax...')

            with mock.patch(
                'time.gmtime',
                return_value=time.struct_time((2016, 1, 18, 20, 50, 36, 0, 18, 0))
            ):
                self.clear_queues()
                self.plugin.cron_go('instagram.butt')
                self.assertNoReplies()

    def test_butt_cron_blocked(self):
        self.test_buttmeon()  # enable buttme

        import mock
        import time

        with mock.patch(
            'time.gmtime',
            return_value=time.struct_time((2016, 1, 18, 13, 50, 36, 0, 18, 0))
        ):
            self.push_fake_result('error', status_code=403)
            self.push_fake_result(True)  # for sendAction
            self.plugin.cron_go('instagram.butt')
            self.assertEqual(self.pop_reply()[1]['caption'], 'Bon appetit!')  # some message was still sent, doesn't really matter
            self.test_buttme()  # check buttme was disabled

    def test_butt_cron_weekend_break(self):
        self.test_buttmeon()

        import mock
        import time

        with mock.patch(
            'time.gmtime',
            return_value=time.struct_time((2016, 1, 17, 13, 50, 36, 5, 18, 0))
        ):
            self.plugin.cron_go('instagram.butt')
            self.assertNoReplies()

    def test_buttgmt(self):
        self.receive_message('/buttgmt +3')
        self.assertReplied('Timezone set to GMT+3')
        self.test_buttmeon(status=u'''\
Butt enabled, use /buttmeoff to disable it.
Your timezone is set to *GMT+3*, use /buttgmt to change it.''')

        import mock
        import time

        with mock.patch(
            'time.gmtime',
            return_value=time.struct_time((2016, 1, 18, 9, 50, 36, 0, 18, 0))
        ):
            self.clear_queues()
            self.plugin.cron_go('instagram.butt')
            self.assertNoReplies()

        with mock.patch(
            'time.gmtime',
            return_value=time.struct_time((2016, 1, 18, 6, 50, 36, 0, 18, 0))
        ):
            self.plugin.cron_go('instagram.butt')
            self.assertEqual(self.pop_reply()[1]['caption'], 'Good morning!')

        self.receive_message('/buttgmt -5')
        self.assertReplied('Timezone set to GMT-5')

        with mock.patch(
            'time.gmtime',
            return_value=time.struct_time((2016, 1, 18, 18, 50, 36, 0, 18, 0))
        ):
            self.plugin.cron_go('instagram.butt')
            self.assertEqual(self.pop_reply()[1]['caption'], 'Bon appetit!')

    def test_buttgmt_validation(self, error_msg='Invalid offset value. It should be a number between -12 and 12 (no half-hour offsets at the moment, apologies to India, Iran, etc)'):
        self.receive_message('/buttgmt')
        self.receive_message('3')
        self.assertReplied('Timezone set to GMT+3')
        self.receive_message('/buttgmt a')
        self.assertReplied(error_msg)
        self.receive_message('/buttgmt -5')
        self.assertReplied('Timezone set to GMT-5')
        self.receive_message('/buttgmt -11.5')
        self.assertReplied(error_msg)
        self.receive_message('/buttgmt 0')
        self.assertReplied('Timezone set to GMT+0')
        self.receive_message('/buttgmt 14')
        self.assertReplied(error_msg)

    def test_broadcast(self):
        self.test_buttmeon()
        self.plugin.save_data('cache', key2='1', obj='2')  # some cache for coverage
        self.plugin.cron_go('instagram.broadcast', 'test 1 2 3')
        self.assertReplied('test 1 2 3')
