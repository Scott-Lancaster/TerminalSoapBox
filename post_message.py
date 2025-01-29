import argparse
import os
import subprocess
import sys
import yaml

import tweepy
from tweepy.errors import TweepyException

from nostr.key import PrivateKey
from nostr.event import Event
from nostr.relay import Relay


def decrypt_config(encrypted_file, decrypted_file):
    """
    Decrypts an encrypted YAML file using GPG silently.
    Suppresses gpg's usual output, only prints if there's an error.
    """
    try:
        subprocess.run(
            ['gpg', '--decrypt', '--output', decrypted_file, encrypted_file],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
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
    """Posts a message to Twitter using Tweepy’s API v2 Client."""
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

def post_to_nostr(nsec_key, message):
    """Posts a message to Nostr using Jeff Thibault’s nostr library."""
    try:
        # 1) Decode your nsec key
        sk = PrivateKey.from_nsec(nsec_key)
        pubkey_hex = sk.public_key.hex()

        # 2) Now pass 'message' as the second argument (content), 
        #    and kind (1) as the third argument if you want a text note
        event = Event(
            pubkey_hex,  # public_key (1st arg)
            message,     # content (2nd arg, must be a str)
            1            # kind = 1 (3rd arg)
        )

        # 3) Sign and publish
        sk.sign_event(event)
        with Relay("wss://relay.primal.net") as relay:
            relay.publish(event)

        print("Message posted to Nostr successfully!")
    except Exception as e:
        print(f"Error posting to Nostr: {e}")


if __name__ == "__main__":
    # 1. Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Post a message to Twitter, Nostr, or both."
    )
    parser.add_argument(
        "--twitter",
        action="store_true",
        help="Post to Twitter only."
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

    # 2. Decrypt the YAML config
    ENCRYPTED_CONFIG_PATH = "config.yaml.gpg"
    DECRYPTED_CONFIG_PATH = "config.yaml"

    decrypt_config(ENCRYPTED_CONFIG_PATH, DECRYPTED_CONFIG_PATH)

    # 3. Load credentials from the decrypted config
    config = load_config(DECRYPTED_CONFIG_PATH)

    # 4. Safely remove the decrypted file
    try:
        os.remove(DECRYPTED_CONFIG_PATH)
    except Exception as e:
        print(f"Error removing decrypted file: {e}")

    # 5. Extract nested dicts
    twitter_config = config.get('twitter', {})
    nostr_config = config.get('nostr', {})

    # 6. Post to Twitter if --twitter is used or no flags are passed
    if args.twitter or (not args.twitter and not args.nostr):
        post_to_twitter(
            twitter_config.get('api_key'),
            twitter_config.get('api_secret_key'),
            twitter_config.get('access_token'),
            twitter_config.get('access_secret'),
            message
        )

    # 7. Post to Nostr if --nostr is used or no flags are passed
    if args.nostr or (not args.twitter and not args.nostr):
        post_to_nostr(
            nostr_config.get('private_key'),
            message
        )
