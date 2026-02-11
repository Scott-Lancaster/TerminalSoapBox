import argparse
import asyncio
import os
import subprocess
import sys
import yaml

import tweepy
from tweepy.errors import TweepyException

from nostr_sdk import Client, Keys, NostrSigner, EventBuilder, RelayUrl


def decrypt_config(encrypted_file, decrypted_file):
    """
    Decrypts an encrypted YAML file using GPG.
    Allows passphrase prompt to appear.
    """
    try:
        subprocess.run(
            ['gpg', '--quiet', '--decrypt', '--output', decrypted_file, encrypted_file],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error decrypting file: {e}")
        sys.exit(1)

def load_config(file_path):
    """
    Loads YAML configuration from a file.
    Returns a dictionary with 'twitter' and 'nostr' credentials.
    """
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading YAML file: {e}")
        sys.exit(1)

def post_to_twitter(api_key, api_secret_key, access_token, access_secret, message):
    """Posts a message to Twitter/X using Tweepy’s API v2 Client."""
    try:
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret_key,
            access_token=access_token,
            access_token_secret=access_secret
        )
        response = client.create_tweet(text=message)
        
        if response and response.data:
            print(f"Tweet posted successfully! Tweet ID: {response.data['id']}")
        else:
            print("Failed to post tweet.")
    except TweepyException as e:
        print(f"Twitter API error: {e}")
    except Exception as e:
        print(f"Unexpected error posting to Twitter: {e}")

async def post_to_nostr_async(nsec_key, message):
    """Asynchronous function to post a message to Nostr using nostr-sdk."""
    try:
        # Parse keys from nsec private key string
        keys = Keys.parse(nsec_key)
        
        # Create signer and client
        signer = NostrSigner.keys(keys)
        client = Client(signer)
        
        # Add multiple relays for better propagation
        relays = [
            "wss://relay.damus.io",
            "wss://nos.lol",
            "wss://relay.snort.social"
        ]
        for url_str in relays:
            relay_url = RelayUrl.parse(url_str)
            await client.add_relay(relay_url)
        
        # Connect to relays
        await client.connect()
        
        # Build and send the text note event (kind 1)
        builder = EventBuilder.text_note(message)
        event_id = await client.send_event_builder(builder)
        
        print("Message posted to Nostr successfully!")
        print(f"Event ID: {event_id.id.to_bech32()}")  # Bech32 format (e.g., note1...)
        
    except Exception as e:
        print(f"Error posting to Nostr: {e}")
    finally:
        # Always disconnect cleanly
        try:
            await client.disconnect()
        except:
            pass

def post_to_nostr(nsec_key, message):
    """Synchronous wrapper for posting to Nostr."""
    asyncio.run(post_to_nostr_async(nsec_key, message))


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Post a message to Twitter/X, Nostr, or both."
    )
    parser.add_argument(
        "--twitter",
        action="store_true",
        help="Post to Twitter/X only."
    )
    parser.add_argument(
        "--nostr",
        action="store_true",
        help="Post to Nostr only."
    )
    parser.add_argument(
        "message",
        nargs="+",
        help="The message to post."
    )
    args = parser.parse_args()
    message = " ".join(args.message)

    # Set absolute paths based on the script's location
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    ENCRYPTED_CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.yaml.gpg")
    DECRYPTED_CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.yaml")

    # Check if encrypted config file exists
    if not os.path.exists(ENCRYPTED_CONFIG_PATH):
        print(f"Error: Encrypted config file not found at {ENCRYPTED_CONFIG_PATH}")
        sys.exit(1)

    # Decrypt the YAML config
    decrypt_config(ENCRYPTED_CONFIG_PATH, DECRYPTED_CONFIG_PATH)

    # Load credentials from the decrypted config
    config = load_config(DECRYPTED_CONFIG_PATH)

    # Safely remove the decrypted file
    try:
        os.remove(DECRYPTED_CONFIG_PATH)
    except Exception as e:
        print(f"Error removing decrypted file: {e}")

    # Extract nested configs
    twitter_config = config.get('twitter', {})
    nostr_config = config.get('nostr', {})

    # Post to Twitter/X if --twitter is used or no flags are passed
    if args.twitter or (not args.twitter and not args.nostr):
        post_to_twitter(
            twitter_config.get('api_key'),
            twitter_config.get('api_secret_key'),
            twitter_config.get('access_token'),
            twitter_config.get('access_secret'),
            message
        )

    # Post to Nostr if --nostr is used or no flags are passed
    if args.nostr or (not args.twitter and not args.nostr):
        post_to_nostr(
            nostr_config.get('private_key'),
            message
        )