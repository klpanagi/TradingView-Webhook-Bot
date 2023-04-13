# ----------------------------------------------- #
# Plugin Name           : TradingView-Webhook-Bot #
# Author Name           : fabston                 #
# File Name             : handler.py              #
# ----------------------------------------------- #

import smtplib
import ssl
from email.mime.text import MIMEText

import tweepy
from discord_webhook import DiscordEmbed, DiscordWebhook
from slack_webhook import Slack
import config
import requests


if config.send_mqtt_alerts:
    from commlib.node import Node
    from commlib.transports.mqtt import ConnectionParameters
    from commlib.msg import MessageHeader, PubSubMessage
    from typing import Dict, Any

    class TradingViewSignal(PubSubMessage):
        header: MessageHeader = MessageHeader()
        data: Any

    mqtt_node = Node(node_name='sensors.sonar.front',
                     connection_params=ConnectionParameters(
                        host=config.mqtt_host,
                        port=config.mqtt_port,
                        username=config.mqtt_username,
                        password=config.mqtt_password
                    ),
                    debug=False)

    mqtt_pub = mqtt_node.create_publisher(msg_type=TradingViewSignal,
                                          topic=config.mqtt_alerts_topic)


def send_to_mqtt(message):
    msg = TradingViewSignal(data=message)
    if mqtt_pub:
        mqtt_pub.publish(msg)


def send_to_telegram(message):
    apiToken = config.tg_token
    chatID = config.channel
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'
    try:
        response = requests.post(apiURL, json={'chat_id': chatID,
                                               'parse_mode': 'MARKDOWN',
                                               'text': message})
        return response
    except Exception as e:
        print(e)


async def send_alert(data):
    msg = data["msg"].encode("latin-1", "backslashreplace").decode("unicode_escape")
    if config.send_telegram_alerts:
        try:
            send_to_telegram(msg)
            print("[*] Telegram Alert sent!")
        except KeyError:
            print("[X] Telegram Error:\n>", e)

    if config.send_discord_alerts:
        try:
            webhook = DiscordWebhook(
                url="https://discord.com/api/webhooks/" + data["discord"]
            )
            embed = DiscordEmbed(title=msg)
            webhook.add_embed(embed)
            webhook.execute()
        except KeyError:
            webhook = DiscordWebhook(
                url="https://discord.com/api/webhooks/" + config.discord_webhook
            )
            embed = DiscordEmbed(title=msg)
            webhook.add_embed(embed)
            webhook.execute()
        except Exception as e:
            print("[X] Discord Error:\n>", e)

    if config.send_slack_alerts:
        try:
            slack = Slack(url="https://hooks.slack.com/services/" + data["slack"])
            slack.post(text=msg)
        except KeyError:
            slack = Slack(
                url="https://hooks.slack.com/services/" + config.slack_webhook
            )
            slack.post(text=msg)
        except Exception as e:
            print("[X] Slack Error:\n>", e)

    if config.send_twitter_alerts:
        tw_auth = tweepy.OAuthHandler(config.tw_ckey, config.tw_csecret)
        tw_auth.set_access_token(config.tw_atoken, config.tw_asecret)
        tw_api = tweepy.API(tw_auth)
        try:
            tw_api.update_status(
                status=msg.replace("*", "").replace("_", "").replace("`", "")
            )
        except Exception as e:
            print("[X] Twitter Error:\n>", e)

    if config.send_email_alerts:
        try:
            email_msg = MIMEText(
                msg.replace("*", "").replace("_", "").replace("`", "")
            )
            email_msg["Subject"] = config.email_subject
            email_msg["From"] = config.email_sender
            email_msg["To"] = config.email_sender
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                config.email_host, config.email_port, context=context
            ) as server:
                server.login(config.email_user, config.email_password)
                server.sendmail(
                    config.email_sender, config.email_receivers, email_msg.as_string()
                )
                server.quit()
        except Exception as e:
            print("[X] Email Error:\n>", e)

    if config.send_mqtt_alerts:
        send_to_mqtt(msg)
        print("[*] MQTT Alert sent!")
