# coding=utf-8

from tgbot import plugintest, webserver
import webtest
import buttiebot


class WebTest(plugintest.PluginTestCase):
    def setUp(self):
        self.bot = self.prepare_bot(bot=buttiebot.setup('sqlite:///:memory:', '123'))
        self.bot.setup_db()
        self.webapp = webtest.TestApp(webserver.wsgi_app([self.bot]))

    def test_web(self):
        self.webapp.post_json('/update/123', params=self.build_message(u'/butt'))
        reply = self.pop_reply()
        self.assertEqual(reply[0], 'sendPhoto')
        self.assertIn('Snorkeled', reply[1]['caption'])
