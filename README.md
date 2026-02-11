# Terminal Soapbox

A Python script that posts messages to **Twitter/X** or **Nostr** from the command line. It stores all secrets (API keys and Nostr `nsec` key) in an **encrypted** YAML file, decrypted on-the-fly with **GPG** to keep your credentials secure.

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
  1. Decrypts a GPG-encrypted `config.yaml.gpg` (which holds Twitter/X and Nostr credentials).  
  2. Posts the given message **either** to Twitter/X, to Nostr, or to both (if no flags provided).  

Key highlights:
1. **GPG Encryption**: Protects your `config.yaml` so credentials are never stored in plaintext.  
2. **Twitter/X Integration**: Uses the **Tweepy** library (API v2 Client) to post tweets.  
3. **Nostr Integration**: Uses the `nostr-sdk` library (Python bindings for rust-nostr) to post text notes (`kind=1`) via your `nsec` private key to multiple relays.  
4. **Flexibility**: Command-line flags `--twitter` and `--nostr` let you post selectively. By default, it posts to both if no flags are specified.

---

## How It Works
1. **Decryption**:  
   - A GPG command decrypts the file `config.yaml.gpg` into `config.yaml`, allowing the passphrase prompt if needed.  
2. **Load Credentials**:  
   - The script reads **Twitter/X** keys (`api_key`, `api_secret_key`, `access_token`, `access_secret`) and **Nostr** key (`private_key`) from the YAML.  
3. **Post to Twitter/X** (optional):  
   - If `--twitter` is passed or no flags are passed, uses Tweepy to create a tweet with the provided text and prints the Tweet ID on success.  
4. **Post to Nostr** (optional):  
   - If `--nostr` is passed or no flags are passed, uses your Nostr `nsec` key to sign and publish a text note (`kind=1`) to multiple relays (e.g., wss://relay.damus.io, wss://nos.lol, wss://relay.snort.social). Prints the Event ID in Bech32 format (e.g., `note1...`) on success.  
5. **Cleanup**:  
   - The script removes the decrypted `config.yaml` after usage for security.

---

## Setup

### Requirements
- **Python 3.7+**  
- **GPG** (GNU Privacy Guard) installed on your system  
- **Python Libraries** (install via `pip` or `pip3`):
  1. `tweepy` (for Twitter/X posting)  
  2. `pyyaml` (for loading config)  
  3. `nostr-sdk` (for Nostr posting)  
- **Twitter/X Developer** credentials for read-write access (API Key, Secret, Access Token, Access Secret).  
- **Nostr `nsec` Private Key**: Generated from a Nostr client (e.g., Damus or nostr.tools).

### Installation
1. **Clone or copy** the `post_message.py` script into your project directory.  
2. **Install** required Python libraries:

   ```bash
   pip3 install tweepy pyyaml nostr-sdk