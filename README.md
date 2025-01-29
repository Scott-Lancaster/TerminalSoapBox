# Terminal Soapbox

A Python script that posts messages to **Twitter** or **Nostr** from the command line. It stores all secrets (API keys and Nostr `nsec` key) in an **encrypted** YAML file, decrypted on-the-fly with **GPG** to keep your credentials secure.

---

## Table of Contents
1. [Summary](#summary)  
2. [How It Works](#how-it-works)  
3. [Setup](#setup)  
   - [Requirements](#requirements)  
   - [Installation](#installation)  
   - [Encrypting Your `config.yaml`](#encrypting-your-configyaml)  
4. [Usage](#usage)  
5. [Optional Shortcut Scripts](#optional-shortcut-scripts)  

---

## Summary
- **Script Name**: `post_message.py`  
- **Purpose**:  
  1. Decrypts a GPG-encrypted `config.yaml.gpg` (which holds Twitter/Nostr credentials).  
  2. Posts the given message **either** to Twitter, to Nostr, or to both (if no flags provided).  

Key highlights:
1. **GPG Encryption**: Protects your `config.yaml` so credentials are never stored in plaintext.  
2. **Twitter Integration**: Uses the **Tweepy** library (API v2 Client) to post tweets.  
3. **Nostr Integration**: Uses Jeff Thibault’s `nostr` library to post text notes (`kind=1`) via your `nsec` private key.  
4. **Flexibility**: Command-line flags `--twitter` and `--nostr` let you post selectively. By default, it posts to both if no flags are specified.

---

## How It Works
1. **Decryption**:  
   - A GPG command decrypts the file `config.yaml.gpg` into `config.yaml`, suppressing normal GPG output.  
2. **Load Credentials**:  
   - The script reads **Twitter** keys (`api_key`, `api_secret_key`, `access_token`, `access_secret`) and **Nostr** key (`private_key`) from the YAML.  
3. **Post to Twitter** (optional):  
   - If `--twitter` is passed or no flags are passed, uses Tweepy to create a tweet with the provided text.  
4. **Post to Nostr** (optional):  
   - If `--nostr` is passed or no flags are passed, uses your Nostr `nsec` key to sign and publish a text note (`kind=1`) to a specified relay.  
5. **Cleanup**:  
   - The script removes the decrypted `config.yaml` after usage for security.

---

## Setup

### Requirements
- **Python 3.7+**  
- **GPG** (GNU Privacy Guard) installed on your system  
- **Python Libraries** (install via `pip` or `pip3`):
  1. `tweepy`  
  2. `pyyaml`  
  3. `nostr` (Jeff Thibault’s library, version `0.0.2` or newer)  
  4. Other dependencies as needed (e.g., `cryptography`, `websocket-client`)
- **Twitter Developer** credentials for read-write access (API Key, Secret, Access Token, Access Secret).

## Bonus Setup
- If you want to create a shortcut so you can just type "tweet 'Hello world'", the steps are below.
      echo '#!/bin/bash' > ~/tweet
      echo 'python3 /path_to/post_message.py --twitter "$@"' >> ~/tweet
      chmod +x ~/tweet 
- repeat for nostr, both, or other protocols that are added.

### Installation
1. **Clone or copy** the `post_message.py` script into your project directory.  
2. **Install** required Python libraries:

   ```bash
   pip3 install tweepy pyyaml nostr
