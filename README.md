    rhc app-create buttiebot python-2.7 postgresql-9.2 cron-1.4 --from-code https://gitlab.com/skmobi/tgbot-buttiebot.git
    rhc env-set TGTOKEN=<YOUR_BOT_TOKEN>
    rhc ssh -- 'app-root/repo/buttiebot.py --db_url="postgresql://$OPENSHIFT_POSTGRESQL_DB_HOST:$OPENSHIFT_POSTGRESQL_DB_PORT/$PGDATABASE" --create_db'
    rhc app-start
