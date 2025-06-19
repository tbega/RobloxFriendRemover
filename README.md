# Roblox Friends & Followers Manager

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt6-Latest-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Mac%20%7C%20Linux-lightgrey.svg)](https://github.com/)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com/)

A clean, modern tool for managing your Roblox friends and followers. Built with PyQt6 for a smooth desktop experience.

## What does this do?

This tool lets you bulk remove friends and followers from your Roblox account. Tired of having hundreds of random people in your friends list? This will clean it up fast.

**Friends removal** - Uses Roblox's unfriend API  
**Followers removal** - Temporarily blocks then unblocks users (removes them as followers without hitting block limits)

## Main Features

- **Clean UI** - Modern dark theme, no clutter
- **Two tabs** - Separate sections for friends and followers  
- **Smart filtering** - Exclude specific users, protect friends from follower removal (and vice versa)
- **Speed control** - Adjust how fast it runs (0.1 to 10 seconds between actions)
- **Real-time updates** - See exactly what's happening as it runs
- **Stop anytime** - Big red stop button if you need to bail

## Setup

Just download `ClearFriends.py` and run it. The script will automatically install what it needs (PyQt6 and requests).

### Getting your cookie

You need your `.ROBLOSECURITY` cookie from Roblox. Here's how:

**Chrome/Edge:**
1. Go to roblox.com and log in
2. Press F12 → Application tab → Cookies → roblox.com
3. Find `.ROBLOSECURITY` and copy the value

**Firefox:**  
1. Go to roblox.com and log in  
2. Press F12 → Storage tab → Cookies → roblox.com
3. Find `.ROBLOSECURITY` and copy the value

**Any browser (console method):**
1. Log into Roblox
2. Press F12 → Console tab
3. Paste: `document.cookie.split(';').find(c => c.includes('.ROBLOSECURITY')).split('=')[1]`
4. Copy the result

⚠️ **Don't share this cookie with anyone** - it's basically your password
- Worried? Everything runs locally on your computer, nothing is saved or sent anywhere. Read the source code if you wish to verify.

## How to use it

### Friends tab
- Paste your cookie
- **Skip removing friends** - Check this to test without actually removing anyone
- **Don't remove followers** - Keeps people who follow you in your friends list  
- **Excluded users** - Type user IDs (one per line) to protect specific people
- Hit start and watch it work

### Followers tab  
- Same setup as friends tab
- **Don't remove friends** - Protects your actual friends from being removed as followers
- Uses block/unblock method so it doesn't hit Roblox's block limit

## What happens behind the scenes

The tool uses Roblox's official APIs:
- Gets your friends/followers lists
- Filters out excluded users
- Removes them one by one with delays to avoid rate limiting
- Shows progress in real-time

For followers, it temporarily blocks then immediately unblocks each person. This removes them as a follower without permanently blocking them.

## Common issues

**"Authentication failed"**  
Your cookie expired. Get a fresh one from your browser.

**"Rate limited"**  
Slow down the speed or take a break. Roblox is telling you to chill.

**Tool freezes**  
Check your internet connection. The tool might be waiting for Roblox to respond.

**No friends/followers found**  
Make sure you actually have friends/followers and that your account settings allow the tool to see them.

## Security stuff

- Everything runs locally on your computer
- Your cookie only goes to Roblox's servers (nowhere else)
- No data is saved or stored anywhere
- You can read the entire source code to verify this

The tool only uses official Roblox API endpoints that your browser would normally use.

---

## 📄 Disclaimer
This is a community tool. Roblox Corporation doesn't make or endorse this.

Use at your own risk. The usual disclaimers apply - I'm not responsible if something goes wrong.

This tool is provided **as-is** for personal use only. Users assume all responsibility for:
- Account safety and security
- Compliance with Roblox Terms of Service  
- Any consequences from tool usage
- Data loss or relationship removal

**Not affiliated with Roblox Corporation.** This is an independent utility tool.

---
