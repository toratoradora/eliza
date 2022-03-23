from core.args import parse, config, get_model_provider
from core.logging import get_logger
from client.bot import TerminalBot, TwitterBot, DiscordBot

import sys
import traceback

logger = get_logger(__name__)

def get_key(dictionary, key, required=True, default=None):
    if key in dictionary:
        return dictionary[key]
    elif required:
        raise Exception(f'{key} is required')
    else:
        return default

def main():
    logger.info('Initializing ELIZA...')

    logger.info('Loading config...')
    chatbot_config = config(parse())
    bot = None
    try:
        logger.info('Getting model provider...')
        model_provider = get_model_provider(chatbot_config)
        if chatbot_config['client'] == 'terminal':
            bot = TerminalBot(name=chatbot_config['name'], model_provider=model_provider)
            logger.info('Starting %s with the terminal as the client...'%chatbot_config['name'])
            bot.run()
        elif chatbot_config['client'] == 'discord':
            bot = DiscordBot(
                name=chatbot_config['name'],
                model_provider=model_provider,
                bearer_token=get_key(chatbot_config['client_args'], 'bearer_token'),
                priority_channel=get_key(chatbot_config['client_args'], 'priority_channel'),
                conditional_response=get_key(chatbot_config['client_args'], 'conditional_response', required=False, default=True),
                idle_messaging=get_key(chatbot_config['client_args'], 'idle_messaging', required=False, default=False),
                idle_messaging_interval=get_key(chatbot_config['client_args'], 'idle_messaging_interval', required=False, default=100),
                nicknames=get_key(chatbot_config['client_args'], 'nicknames'),
                status=get_key(chatbot_config['client_args'], 'status', required=False, default=None),
                context_size=get_key(chatbot_config['client_args'], 'context_size', required=False, default=924),
            )
            logger.info('Starting %s with Discord as the client...'%chatbot_config['name'])
            bot.run()
        elif chatbot_config['client'] == 'twitter':
            bot = TwitterBot(
                name=chatbot_config['name'],
                model_provider=model_provider,
                bearer_token=chatbot_config['client_args']['bearer_token'],
                consumer_key=chatbot_config['client_args']['consumer_key'],
                consumer_secret=chatbot_config['client_args']['consumer_secret'],
                access_token=chatbot_config['client_args']['access_token'],
                access_token_secret=chatbot_config['client_args']['access_token_secret'],
                username=chatbot_config['client_args']['username'],
                tweet_example=chatbot_config['client_args']['tweet_example']
            )
            logger.info('Starting %s with Twitter as the client...'%chatbot_config['name'])
            bot.run()
        else:
            raise Exception('unsupported client')
    except KeyboardInterrupt:
        print('Exiting...')
        bot.close()
        sys.exit(0)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        bot.close()
        sys.exit(1)
    finally:
        logger.info('Exiting...')
        bot.close()
        sys.exit(0)

if __name__ == '__main__':
    main()
