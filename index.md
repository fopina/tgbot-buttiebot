---
layout: index
---

xThis is a friendly Telegram bot that will cheer your day, feel free to contact [@ButtieBot](http://telegram.me/buttiebot).

[![Build Status](https://travis-ci.org/fopina/tgbot-buttiebot.svg?branch=master)](https://travis-ci.org/fopina/tgbot-buttiebot) [![Coverage Status](https://coveralls.io/repos/fopina/tgbot-buttiebot/badge.svg?branch=master&service=github)](https://coveralls.io/github/fopina/tgbot-buttiebot?branch=master)

ButtieBot was a developed using [TGBotPlug](http://fopina.github.io/tgbotplug).

This repository is ready for openshift (as the bot is running there), so you can easily host your own:

* Register in [OpenShift](https://www.openshift.com)  
* Install [rhc](https://developers.openshift.com/en/managing-client-tools.html), the command line tool  
* Run `rhc setup` to configure it  
* Talk to [@BotFather](http://telegram.me/botfather) to register your bot  
* And finally run these commands (replacing `<YOUR_BOT_TOKEN>` with the token provided by @BotFather)

    ```
    rhc app-create buttiebot python-2.7 postgresql-9.2 cron-1.4 --from-code https://github.com/fopina/tgbot-buttiebot/
    cd buttiebot
    rhc env-set TGTOKEN=<YOUR_BOT_TOKEN>
    rhc ssh -- 'app-root/repo/buttiebot.py --db_url="postgresql://$OPENSHIFT_POSTGRESQL_DB_HOST:$OPENSHIFT_POSTGRESQL_DB_PORT/$PGDATABASE" --create_db'
    rhc app-restart
    ```
    
Have fun!
