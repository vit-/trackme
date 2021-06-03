import os
import logging
from datetime import datetime, timedelta
from uuid import uuid4

from elasticsearch import Elasticsearch
from telegram import error, Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PicklePersistence

from trackme_bot import data
from trackme_bot.config import Config


DEFAULT_LIVE_PERIOD_SECS = 30 * 60
DEFAULT_LIVE_INTERVAL_SECS = 30

TELEMETRY_STALE_AGE = timedelta(minutes=5)
TELEMETRY_CHECK_INTERVAL_SECS = 60

AUTH_KEY = 'auth'
TELEMETRY_ALERT_KEY = 'alert_telemetry'


logger = logging.getLogger(__name__)


def require_auth(handler):
    def wrapper(update: Update, context: CallbackContext):
        authed_users = context.bot_data.get(AUTH_KEY) or []
        if update.effective_user not in authed_users:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Unauthorized')
            return
        return handler(update, context)
    return wrapper


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def auth(update: Update, context: CallbackContext):
    args = context.args
    if len(args) != 1:
        logger.warning('Authorization failed: [%s] "%s"', update.effective_user, update.effective_message.text)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Malformed command')
        return

    token = args[0]
    if token != context.dispatcher.config.auth_token:
        logger.warning('Authorization failed: [%s] "%s"', update.effective_user, update.effective_message.text)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Invalid token')
        return

    if AUTH_KEY not in context.bot_data:
        context.bot_data[AUTH_KEY] = []

    for user in context.bot_data[AUTH_KEY]:
        context.bot.send_message(chat_id=user.id, text='{} has been authorized'.format(update.effective_user.name))

    context.bot_data[AUTH_KEY].append(update.effective_user)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Authorized')
    logger.info('Authorized: [%s]', update.effective_user)


@require_auth
def deauth(update: Update, context: CallbackContext):
    new_token = str(uuid4())
    context.dispatcher.config.auth_token = new_token
    del context.bot_data[AUTH_KEY]
    context.bot.send_message(chat_id=update.effective_chat.id, text='Deauthed all users')
    context.bot.send_message(chat_id=update.effective_chat.id, text=new_token)


@require_auth
def auth_list(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='\n'.join([user.name for user in context.bot_data[AUTH_KEY]]),
    )


@require_auth
def location(update: Update, context: CallbackContext):
    es: Elasticsearch = context.dispatcher.config.es
    loc = data.get_last_location(es)
    if loc is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Live location is not available')
        return

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Latest location date: {loc.date}',
    )

    message = context.bot.send_location(
        chat_id=update.effective_chat.id,
        latitude=loc.lat,
        longitude=loc.lon,
        live_period=DEFAULT_LIVE_PERIOD_SECS,
    )

    def update_location(ctx: CallbackContext):
        loc = data.get_last_location(es)
        try:
            ctx.bot.edit_message_live_location(
                chat_id=message.chat_id,
                message_id=message.message_id,
                longitude=loc.lon,
                latitude=loc.lat,
            )
        except error.BadRequest as ex:
            if str(ex) == "Message can't be edited":
                ctx.job.schedule_removal()

    context.job_queue.run_repeating(update_location, interval=DEFAULT_LIVE_INTERVAL_SECS)


def format_trip(trip: data.Trip) -> str:
    return f'<b>{trip.start_date.strftime("%Y-%m-%d")}</b> {trip.start_date.strftime("%H:%M")} - {trip.stop_date.strftime("%H:%M")}'


@require_auth
def trips(update: Update, context: CallbackContext):
    trips = data.get_trips(context.dispatcher.config.es)
    msg = '\n'.join(format_trip(trip) for trip in trips)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        parse_mode=ParseMode.HTML,
        text=msg,
    )


def check_telemetry_health(context: CallbackContext):
    authed_users = context.bot_data.get(AUTH_KEY)
    if not authed_users:
        logger.info('No authed users, skipping telemetry health check')
        return

    loc = data.get_last_location(context.dispatcher.config.es)
    if loc is None or (datetime.utcnow() - loc.date) > TELEMETRY_STALE_AGE:
        logger.warning('Telemetry unhealthy, location: %s', loc)

        if not context.bot_data.get(TELEMETRY_ALERT_KEY):
            context.bot_data[TELEMETRY_ALERT_KEY] = True
            for user in authed_users:
                context.bot.send_message(
                    chat_id=user.id,
                    text='Stopped receiving telemetry data'
                )
    else:
        logger.info('Telemetry health OK')
        if TELEMETRY_ALERT_KEY in context.bot_data:
            del context.bot_data[TELEMETRY_ALERT_KEY]
            for user in authed_users:
                context.bot.send_message(
                    chat_id=user.id,
                    text='Telemetry is back online '
                )

def setup_logging():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)


def main():
    tg_token = os.environ['TRACKME_TG_TOKEN']
    auth_token = os.environ['TRACKME_AUTH_TOKEN']
    persistence_filename = os.environ.get('TRACKME_PERSISTENCE_FILENAME', 'bot.state')
    es_host = os.environ['TRACKME_ES_HOST']
    es_username = os.environ.get('TRACKME_ES_USER')
    es_password = os.environ.get('TRACKME_ES_PASSWORD')
    es_scheme = os.environ.get('TRACKME_ES_SCHEME', 'http')
    es_port = int(os.environ.get('TRACKME_ES_PORT', 9200))

    es_http_auth = None
    if es_username and es_password:
        es_http_auth = (es_username, es_password)

    config = Config(
        auth_token=auth_token,
        es=Elasticsearch(
            hosts=[es_host],
            http_auth=es_http_auth,
            scheme=es_scheme,
            port=es_port,
        ),
    )
    persistence = PicklePersistence(filename=persistence_filename)

    updater = Updater(token=tg_token, use_context=True, persistence=persistence)
    dispatcher = updater.dispatcher
    dispatcher.config = config

    dispatcher.job_queue.run_repeating(check_telemetry_health, interval=TELEMETRY_CHECK_INTERVAL_SECS, first=0)

    dispatcher.add_handler(CommandHandler('auth', auth))
    dispatcher.add_handler(CommandHandler('auth_list', auth_list))
    dispatcher.add_handler(CommandHandler('deauth', deauth))
    dispatcher.add_handler(CommandHandler('location', location))
    dispatcher.add_handler(CommandHandler('trips', trips))

    dispatcher.add_handler(MessageHandler(Filters.all, unknown))

    updater.start_polling()
    updater.idle()

    config.es.close()



if __name__ == '__main__':
    setup_logging()
    main()
