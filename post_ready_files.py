#!/usr/bin/env python3
"""
Simple script to post all READY_*.md files to Ayrshare
Usage: python post_ready_files.py
"""
import os
import glob
import requests
import re

# Configuration
AYRSHARE_API_KEY = "7D248853-8AF94A41-A48F07DC-73F74D88"
REPO_BASE_URL = "https://raw.githubusercontent.com/Alexandria-s-Design/modelit-social-media-assets/main"
POSTS_DIR = "facebook-posts"

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown"""
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        return None, content

    frontmatter_text = match.group(1)
    body = match.group(2).strip()

    frontmatter = {}
    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    return frontmatter, body

def post_to_ayrshare(post_text, image_filename):
    """Post to Ayrshare with auto-schedule"""
    image_url = f"{REPO_BASE_URL}/{POSTS_DIR}/{image_filename}"

    response = requests.post(
        "https://api.ayrshare.com/api/post",
        headers={
            "Authorization": f"Bearer {AYRSHARE_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "post": post_text,
            "platforms": ["facebook"],
            "mediaUrls": [image_url],
            "autoSchedule": {
                "schedule": True,
                "title": "every_other_day"
            }
        }
    )

    return response.json()

def main():
    # Find all READY_*.md files
    ready_files = glob.glob(f"{POSTS_DIR}/READY_*.md")

    if not ready_files:
        print("❌ No READY_*.md files found.")
        print("💡 Create files like: READY_your-topic.md")
        return

    print(f"🔍 Found {len(ready_files)} post(s) ready to schedule:\n")
    for file in ready_files:
        print(f"   ✅ {os.path.basename(file)}")

    print("\n📤 Posting to Ayrshare...\n")

    posted_count = 0
    for filepath in ready_files:
        filename = os.path.basename(filepath)

        # Read file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract frontmatter and post text
        frontmatter, post_text = extract_frontmatter(content)

        if not frontmatter or 'image' not in frontmatter:
            print(f"   ⚠️  {filename}: Missing image in frontmatter, skipping")
            continue

        image_filename = frontmatter['image']

        # Post to Ayrshare
        try:
            result = post_to_ayrshare(post_text, image_filename)

            if result.get('status') == 'scheduled':
                post_id = result['id']
                schedule_date = result['scheduleDate']
                print(f"   ✅ {filename}")
                print(f"      Post ID: {post_id}")
                print(f"      Scheduled: {schedule_date}\n")

                # Rename file to POSTED_
                new_filepath = filepath.replace('READY_', 'POSTED_')
                os.rename(filepath, new_filepath)
                posted_count += 1
            else:
                print(f"   ❌ {filename}: {result.get('message', 'Unknown error')}\n")

        except Exception as e:
            print(f"   ❌ {filename}: Error - {str(e)}\n")

    print(f"\n🎉 Success! {posted_count} post(s) scheduled.")
    if posted_count > 0:
        print("   Posts renamed to POSTED_* prefix.")

if __name__ == "__main__":
    main()
