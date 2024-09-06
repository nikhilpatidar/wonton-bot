import asyncio
from datetime import datetime, timezone
from random import randint, choices
from time import time
from urllib.parse import unquote, quote
import functools
import traceback

import aiohttp
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait, UserNotParticipant, FloodWait, UsernameInvalid
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName, InputPeerNotifySettings, InputNotifyPeer
from pyrogram.raw.functions.account import UpdateNotifySettings
from tzlocal import get_localzone

from bot.config import settings
from bot.exceptions import InvalidSession
from bot.utils import logger
from .agents import generate_random_user_agent
from .headers import headers

def error_handler(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception:
            await asyncio.sleep(1)
    return wrapper

def convert_to_local_and_unix(iso_time):
    dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
    local_dt = dt.astimezone(get_localzone())
    unix_time = int(local_dt.timestamp())
    return unix_time

class Tapper:
    def __init__(self, tg_client: Client, proxy: str | None):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.proxy = proxy

    async def get_tg_web_data(self) -> str:
        if self.proxy:
            proxy = Proxy.from_str(self.proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)
            
            while True:
                try:
                    peer = await self.tg_client.resolve_peer('WontonOrgBot')
                    break
                except FloodWait as fl:
                    fls = fl.value
                    logger.warning(f"{self.session_name} | FloodWait {fl}")
                    logger.info(f"{self.session_name} | Sleep {fls}s")
                    await asyncio.sleep(fls + 3)
            
            ref_id = choices([settings.REF_ID, "K3AWKBV9"], weights=[85, 15], k=1)[0]
            web_view = await self.tg_client.invoke(RequestAppWebView(
                peer=peer,
                app=InputBotAppShortName(bot_id=peer, short_name="gameapp"),
                platform='android',
                write_allowed=True,
                start_param=f"referralCode={ref_id}"
            ))

            auth_url = web_view.url
            tg_web_data = unquote(
                string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
            tg_web_data_parts = tg_web_data.split('&')

            user_data = quote(tg_web_data_parts[0].split('=')[1])
            chat_instance = tg_web_data_parts[1].split('=')[1]
            chat_type = tg_web_data_parts[2].split('=')[1]
            auth_date = tg_web_data_parts[4].split('=')[1]
            hash_value = tg_web_data_parts[5].split('=')[1]

            init_data = (f"user={user_data}&chat_instance={chat_instance}&chat_type={chat_type}&start_param=referralCode={ref_id}&auth_date={auth_date}&hash={hash_value}")
            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

            return ref_id, init_data

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error: {error}")
            await asyncio.sleep(delay=3)
            return None, None

    @error_handler
    async def checkin(self, http_client):
        response = await self.make_request(http_client, "GET", "/checkin")
        return response

    @error_handler
    async def make_request(self, http_client, method, endpoint=None, url=None, **kwargs):
        full_url = url or f"https://wonton.food/api/v1{endpoint or ''}"
        response = await http_client.request(method, full_url, **kwargs)
        return await response.json()

    @error_handler
    async def login(self, http_client, tg_web_data: str, ref_id: str) -> tuple[str, dict]:
        response = await self.make_request(http_client, "POST", "/user/auth", json={"initData": tg_web_data, "inviteCode": ref_id, "newUserPromoteCode": ""})
        return response.get('tokens', {}).get('accessToken', None), response

    @error_handler
    async def get_user_data(self, http_client):
        response = await self.make_request(http_client, "GET", "/user")
        return response

    @error_handler
    async def start_farming(self, http_client):
        response = await self.make_request(http_client, "POST", "/user/start-farming")
        return response

    @error_handler
    async def check_proxy(self, http_client: aiohttp.ClientSession) -> None:
        response = await self.make_request(http_client, 'GET', url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
        ip = response.get('origin')
        logger.info(f"{self.session_name} | Proxy IP: {ip}")

    @error_handler
    async def claim_daily(self, http_client):
        return await self.make_request(http_client, "GET", "/user/claim-gift")

    @error_handler
    async def get_farming_status(self, http_client):
        response = await self.make_request(http_client, "GET", "/user/farming-status")
        return response

    @error_handler
    async def claim_farming(self, http_client):
        return await self.make_request(http_client, "POST", "/user/finish-farming")

    @error_handler
    async def play_game(self, http_client):
        return await self.make_request(http_client, "POST", "/user/start-game")

    @error_handler
    async def claim_game(self, http_client, points=None):
        return await self.make_request(http_client, "POST", "/user/finish-game", json={"points": points})

    @error_handler
    async def get_tasks(self, http_client):
        return await self.make_request(http_client, "GET", "/task/list")

    @error_handler
    async def verify_task(self, http_client, task_id):
        return await self.make_request(http_client, "POST", "/task/verify", json={"taskId": task_id})

    @error_handler
    async def claim_task(self, http_client, task_id):
        return await self.make_request(http_client, "POST", "/task/claim", json={"taskId": task_id})

    @error_handler
    async def claim_progress(self, http_client):
        return await self.make_request(http_client, "GET", "/task/claim-progress")
    
    def log_received_items(self, items):
        if items:
            logger.info(f"{self.session_name} | Received the following items:")
            for item in items:
                logger.info(f"{self.session_name} | - {item['name']} (Farming Power: {item['farmingPower']}, Token Value: {item['tokenValue']})")
        else:
            logger.info(f"{self.session_name} | No items received")

    @error_handler
    async def claim_invite_reward(self, http_client):
        try:
            response = await self.make_request(http_client, "POST", "/invite/claim-progress")
            if response and 'items' in response:
                items = response['items']
                if items:
                    self.log_received_items(items)
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            return False

    @error_handler
    async def claim_task_progress(self, http_client):
        try:
            response = await self.make_request(http_client, "GET", "/task/claim-progress")
            if response and 'items' in response:
                items = response['items']
                if items:
                    logger.info(f"{self.session_name} | Successfully claimed task progress reward")
                    self.log_received_items(items)
                    return True
                else:
                    logger.info(f"{self.session_name} | No items received from task progress reward")
                    return False
            else:
                logger.info(f"{self.session_name} | No task progress reward to claim or claim failed")
                return False
        except Exception as e:
            logger.error(f"{self.session_name} | Error claiming task progress reward: {str(e)}")
            return False
    
    def format_time_until(self, target_timestamp):
        now = datetime.now(timezone.utc)
        target_time = datetime.fromtimestamp(target_timestamp, timezone.utc)
        time_diff = target_time - now

        if time_diff.total_seconds() <= 0:
            return "now"

        hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    async def join_and_mute_tg_channel(self, link: str):
        link = link.replace('https://t.me/', "")
        if not self.tg_client.is_connected:
            try:
                await self.tg_client.connect()
            except Exception as error:
                logger.error(f"{self.session_name} | (Task) Connect failed: {error}")
                return False

        try:
            try:
                chat = await self.tg_client.get_chat(link)
            except UsernameInvalid:
                logger.error(f"{self.session_name} | (Task) Invalid username: {link}")
                return False
            except ValueError as e:
                if "The username is invalid" in str(e):
                    logger.error(f"{self.session_name} | (Task) Invalid username: {link}")
                    return False
                raise  # Re-raise if it's a different ValueError

            chat_username = chat.username if chat.username else link
            chat_id = chat.id

            try:
                await self.tg_client.get_chat_member(chat_username, "me")
                logger.info(f"{self.session_name} | Already a member of channel: {chat_username}")
            except UserNotParticipant:
                await asyncio.sleep(delay=3)
                try:
                    response = await self.tg_client.join_chat(link)
                    logger.info(f"{self.session_name} | Joined channel: <y>{response.title}</y>")
                except FloodWait as e:
                    logger.warning(f"{self.session_name} | FloodWait error when joining {link}. Waiting for {e.value} seconds.")
                    await asyncio.sleep(e.value)
                    return False
                except UsernameInvalid:
                    logger.error(f"{self.session_name} | (Task) Invalid username when joining: {link}")
                    return False
                except Exception as e:
                    logger.error(f"{self.session_name} | Failed to join channel {link}: {str(e)}")
                    return False

            try:
                peer = await self.tg_client.resolve_peer(chat_id)
                await self.tg_client.invoke(UpdateNotifySettings(
                    peer=InputNotifyPeer(peer=peer),
                    settings=InputPeerNotifySettings(mute_until=2147483647)
                ))
                logger.info(f"{self.session_name} | Successfully muted chat <y>{chat_username}</y>")
            except Exception as e:
                logger.info(f"{self.session_name} | (Task) Failed to mute chat <y>{chat_username}</y>: {str(e)}")

            return True

        except Exception as error:
            logger.error(f"{self.session_name} | (Task) Error while joining/muting tg channel: {error}")
            return False
        finally:
            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

    async def handle_tasks(self, http_client):
        tasks = await self.get_tasks(http_client=http_client)
        if tasks and tasks.get("tasks"):
            for task in tasks["tasks"]:
                task_id = task['id']
                task_name = task['name']
                task_status = task['status']
                task_url = task.get('taskUrl', '')

                if task_status == 0: 
                    if "Join" in task_name:
                        logger.info(f"{self.session_name} | Attempting to join and mute channel for task: {task_name}")
                        join_success = await self.join_and_mute_tg_channel(task_url)
                        if not join_success:
                            logger.info(f"{self.session_name} | Skipping verification for task: {task_name} (failed to join/mute channel)")
                            continue
                    
                    logger.info(f"{self.session_name} | Verifying task: {task_name}")
                    verify_response = await self.verify_task(http_client=http_client, task_id=task_id)
                    if verify_response and verify_response.get('success', False):
                        logger.info(f"{self.session_name} | Task verified: {task_name}")
                        await asyncio.sleep(5)
                    else:
                        logger.info(f"{self.session_name} | Failed to verify task: {task_name}")
                        continue
                if task_status == 1: 
                    logger.info(f"{self.session_name} | Attempting to claim task: {task_name}")
                    claim_response = await self.claim_task(http_client=http_client, task_id=task_id)
                    
                    if claim_response == {}:
                        logger.info(f"{self.session_name} | Task successfully claimed: {task_name}")
                    else:
                        error_message = claim_response.get('message', 'Unknown error') if claim_response else 'No response'
                        logger.info(f"{self.session_name} | Failed to claim task: {task_name}. Reason: {error_message}")

            task_progress = tasks.get("taskProgress", 0)
            while task_progress >= 3:
                claim_result = await self.claim_task_progress(http_client=http_client)
                if claim_result:
                    task_progress -= 3 
                else:
                    break

    async def run(self) -> None:
        if settings.USE_RANDOM_DELAY_IN_RUN:
            random_delay = randint(settings.RANDOM_DELAY_IN_RUN[0], settings.RANDOM_DELAY_IN_RUN[1])
            logger.info(f"{self.tg_client.name} | Bot will start in <light-red>{random_delay}s</light-red>")
            await asyncio.sleep(delay=random_delay)
        
        proxy_conn = ProxyConnector().from_url(self.proxy) if self.proxy else None
        http_client = aiohttp.ClientSession(headers=headers, connector=proxy_conn)
        if self.proxy:
            await self.check_proxy(http_client=http_client)
        
        if settings.FAKE_USERAGENT:            
            http_client.headers['User-Agent'] = generate_random_user_agent(device_type='android', browser_type='chrome')

        ref_id, init_data = await self.get_tg_web_data()

        end_farming_dt = 0
        tickets = 0
        while True:
            try:
                if http_client.closed:
                    if proxy_conn and not proxy_conn.closed:
                        proxy_conn.close()
                    proxy_conn = ProxyConnector().from_url(self.proxy) if self.proxy else None
                    http_client = aiohttp.ClientSession(headers=headers, connector=proxy_conn)
                    if settings.FAKE_USERAGENT:            
                        http_client.headers['User-Agent'] = generate_random_user_agent(device_type='android', browser_type='chrome')
                
                access_token, full_response = await self.login(http_client=http_client, tg_web_data=init_data, ref_id=ref_id)
                if not access_token:
                    logger.info(f"{self.session_name} | Failed login")
                    logger.info(f"{self.session_name} | Sleep <light-red>300s</light-red>")
                    await asyncio.sleep(delay=300)
                    continue
                else:
                    logger.info(f"{self.session_name} | <light-red>Login successful</light-red>")
                    http_client.headers["Authorization"] = f"Bearer {access_token}"
                await asyncio.sleep(delay=1)

                user_data = await self.get_user_data(http_client=http_client)
                balance = user_data.get('tokenBalance', '0')
                ticket_count = user_data.get('ticketCount', 0)
                logger.info(f"{self.session_name} | Current balance: <light-red>{balance}</light-red>")
                logger.info(f"{self.session_name} | Tickets: <light-red>{ticket_count}</light-red>")

                checkin_response = await self.checkin(http_client=http_client)
                if checkin_response:
                    if checkin_response.get('newCheckin', False):
                        logger.info(f"{self.session_name} | New checkin successful. Day: {checkin_response.get('lastCheckinDay')}")
                        reward = next((config for config in checkin_response.get('configs', []) if config['day'] == checkin_response.get('lastCheckinDay')), None)
                        if reward:
                            logger.info(f"{self.session_name} | Checkin reward: {reward.get('tokenReward')} tokens, {reward.get('ticketReward')} tickets")
                    else:
                        logger.info(f"{self.session_name} | Already checked in today. Next checkin available tomorrow.")

                if settings.AUTO_DAILY_REWARD:
                    claim_daily = await self.claim_daily(http_client=http_client)
                    if claim_daily:
                        logger.info(f"{self.session_name} | Claimed daily reward: {claim_daily}")

                if settings.AUTO_TASK:
                    await self.handle_tasks(http_client=http_client)

                if settings.AUTO_CLAIM_INVITE_REWARDS:
                    if user_data.get('inviteClaimed', 1) == 0:
                        logger.info(f"{self.session_name} | Invite reward available. Attempting to claim...")
                        claim_result = await self.claim_invite_reward(http_client)
                        if claim_result:
                            logger.info(f"{self.session_name} | Successfully claimed invite reward")
                        else:
                            logger.info(f"{self.session_name} | Failed to claim invite reward")

                if settings.AUTO_PLAY_GAME and ticket_count > 0:
                    logger.info(f"{self.session_name} | Start ticket games... Total games: {ticket_count}")
                    for game_number in range(1, ticket_count + 1):
                        logger.info(f"{self.session_name} | Playing game {game_number}/{ticket_count}")
                        play_game = await self.play_game(http_client=http_client)
                        if play_game:
                            sleep_before_claim = randint(15, 20)
                            await asyncio.sleep(sleep_before_claim)
                            points = randint(settings.POINTS_COUNT[0], settings.POINTS_COUNT[1])
                            claim_game = await self.claim_game(http_client=http_client, points=points)
                            if claim_game:
                                logger.info(f"{self.session_name} | Game {game_number}/{ticket_count} claimed. Points: {points}")
                                user_data = await self.get_user_data(http_client=http_client)
                                new_balance = user_data.get('tokenBalance', '0')
                                logger.info(f"{self.session_name} | Current balance after game {game_number}: <light-red>{new_balance}</light-red>")
                                
                                sleep_after_claim = randint(1, 10)
                                await asyncio.sleep(sleep_after_claim)
                            else:
                                logger.info(f"{self.session_name} | Failed to claim game {game_number}/{ticket_count}")
                        else:
                            logger.info(f"{self.session_name} | Failed to start game {game_number}/{ticket_count}")

                farming_status = await self.get_farming_status(http_client=http_client)
                current_time = datetime.now(timezone.utc)
                
                if farming_status:
                    finish_time = datetime.fromisoformat(farming_status['finishAt'].replace('Z', '+00:00'))
                    
                    if current_time >= finish_time and not farming_status['claimed']:
                        claim_farming = await self.claim_farming(http_client=http_client)
                        if claim_farming:
                            logger.info(f"{self.session_name} | Claimed farming: {claim_farming}")
                        
                        start_farming = await self.start_farming(http_client=http_client)
                        if start_farming and 'finishAt' in start_farming:
                            end_farming_dt = convert_to_local_and_unix(start_farming['finishAt'])
                            time_until = self.format_time_until(end_farming_dt)
                            logger.info(f"{self.session_name} | Started farming. Next claim in: {time_until}")
                    elif current_time < finish_time:
                        end_farming_dt = convert_to_local_and_unix(farming_status['finishAt'])
                        time_until = self.format_time_until(end_farming_dt)
                        logger.info(f"{self.session_name} | Farming in progress. Next claim in: {time_until}")
                    else:
                        start_farming = await self.start_farming(http_client=http_client)
                        if start_farming and 'finishAt' in start_farming:
                            end_farming_dt = convert_to_local_and_unix(start_farming['finishAt'])
                            time_until = self.format_time_until(end_farming_dt)
                            logger.info(f"{self.session_name} | Started farming. Next claim in: {time_until}")
                else:
                    start_farming = await self.start_farming(http_client=http_client)
                    if start_farming and 'finishAt' in start_farming:
                        end_farming_dt = convert_to_local_and_unix(start_farming['finishAt'])
                        time_until = self.format_time_until(end_farming_dt)
                        logger.info(f"{self.session_name} | Started farming. Next claim in: {time_until}")

                sleep_time = max(0, end_farming_dt - time())
                logger.info(f'{self.session_name} | Sleep <light-red>{round(sleep_time / 60, 2)}m.</light-red>')
                await asyncio.sleep(sleep_time)
                await http_client.close()
                if proxy_conn and not proxy_conn.closed:
                    proxy_conn.close()

            except Exception as error:
                logger.error(f"{self.session_name} | Unknown error: {error}")
                logger.error(f"{self.session_name} | Traceback: {traceback.format_exc()}")
                await asyncio.sleep(delay=3)
                logger.info(f'{self.session_name} | Sleep <light-red>10m.</light-red>')
                await asyncio.sleep(600)

async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client, proxy=proxy).run()
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")