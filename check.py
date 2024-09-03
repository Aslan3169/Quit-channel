from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.types import ChannelParticipantsAdmins
import asyncio

api_id = '5827434'
api_hash = '46108f6418ddf95d32064f334b20340f'
channel_id = -1002149770267  # Updated channel ID

client = TelegramClient('session_name', api_id, api_hash)

async def get_admin_ids():
    """Fetch the admin IDs of the channel."""
    admin_ids = set()
    async with client:
        async for participant in client.iter_participants(channel_id, filter=ChannelParticipantsAdmins()):
            admin_ids.add(participant.id)
    return admin_ids

async def fetch_channel_members():
    previous_array = []
    user_print_count = {}  # Track how many times user has been printed
    admin_ids = await get_admin_ids()  # Fetch admin IDs

    async with client:
        while True:
            try:
                # Fetch channel participants
                participants = []
                async for user in client.iter_participants(channel_id):
                    participants.append({
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'phone': user.phone
                    })

                current_ids = {user['id'] for user in participants}
                previous_ids = {user['id'] for user in previous_array}

                # Find users that are in the current array but not in the previous array
                new_users_ids = current_ids - previous_ids
                new_users = [user for user in participants if user['id'] in new_users_ids]

                # Process new users
                for user in new_users:
                    username = user['username']
                    if username:
                        if username in user_print_count:
                            user_print_count[username] += 1
                        else:
                            user_print_count[username] = 1

                        if user_print_count[username] > 1 and user['id'] not in admin_ids:
                            # Attempt to remove the user from the channel
                            try:
                                await client.kick_participant(channel_id, user['id'])
                                print(f"User {user['username']} has been kicked out of the channel.")
                            except FloodWaitError as e:
                                print(f"Rate limit exceeded. Waiting for {e.seconds} seconds.")
                                await asyncio.sleep(e.seconds)
                        elif user_print_count[username] == 1:
                            # Handle new user (first appearance)
                            print(f"User added: {user['username']} - First appearance.")

                # Move current array to previous array
                previous_array = participants

            except Exception as e:
                print(f"Error: {e}")

            # Wait for 1 second before fetching again
            await asyncio.sleep(1)

async def main():
    async with client:
        await fetch_channel_members()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
