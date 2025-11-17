# 🎯 Simple Workflow: GitHub → Ayrshare

**Direct pipeline: Write posts in GitHub → Run 1 command → Auto-scheduled to Facebook**

---

## 📋 THE WORKFLOW (3 Steps)

### Step 1: Create Post Files in GitHub

**Location**: `/facebook-posts/READY_[topic].md`

**Format**:
```markdown
---
status: READY
image: 2025-11-20_facebook_teacher-tip_v1.png
---

🎯 Your post text here...

Multiple paragraphs work fine.

👉 Call to action
📚 Links

#Hashtags #Here
```

**Naming Convention**:
- `READY_` prefix = Ready to post
- `DRAFT_` prefix = Not ready yet
- Script only posts files starting with `READY_`

### Step 2: Add Image (if needed)

**If you already have an image**:
- Upload to `/facebook-posts/` folder
- Reference filename in markdown frontmatter

**If you need to generate an image**:
```bash
cd /workspace/repos/modelit-social-media-assets
python /workspace/scripts/generate_single_image.py "your image prompt here"
# Saves to facebook-posts/ with auto-generated filename
```

### Step 3: Post to Ayrshare

**Run one command**:
```bash
cd /workspace/repos/modelit-social-media-assets
python post_ready_files.py
```

**What it does**:
1. Finds all `READY_*.md` files
2. Extracts post text and image filename
3. Posts to Ayrshare with auto-schedule (every 2 days)
4. Renames file to `POSTED_*.md` so it doesn't post twice
5. Shows summary of posted content

---

## 🚀 COMPLETE EXAMPLE

### 1. Create the post file

**File**: `/facebook-posts/READY_teacher-time-saver.md`
```markdown
---
status: READY
image: 2025-11-20_facebook_teacher-tip_v1.png
---

👩‍🏫 Teachers: Stop spending hours creating lesson plans from scratch.

Our ModelIt K12 lessons are:
• NGSS-aligned and ready to use
• No coding experience required
• Includes student worksheets and assessments
• Free to get started

Save 5+ hours per week on lesson prep.

👉 Get free lessons: https://www.teacherspayteachers.com/store/modelit
📚 Learn more: modelitk12.com

#TeacherLife #STEMEducation #ModelItK12
```

### 2. Generate image (if needed)

```bash
cd /workspace/repos/modelit-social-media-assets
python /workspace/scripts/generate_single_image.py "Educational illustration showing a teacher at desk with clock showing saved time, surrounded by ready-to-use lesson materials, modern flat design, warm colors"
```

Output: `2025-11-20_facebook_teacher-tip_v1.png` (automatically saved to repo)

### 3. Post everything

```bash
cd /workspace/repos/modelit-social-media-assets
python post_ready_files.py
```

**Output**:
```
🔍 Found 1 post ready to schedule:
   ✅ READY_teacher-time-saver.md

📤 Posting to Ayrshare...
   ✅ Post ID: abc123xyz
   📅 Scheduled: 2025-11-21 09:00 AM

🎉 Success! 1 post scheduled.
   Posts renamed to POSTED_* prefix.
```

---

## 📁 FOLDER STRUCTURE

```
modelit-social-media-assets/
├── facebook-posts/
│   ├── DRAFT_systems-thinking-tip-2.md      # Not ready, ignored by script
│   ├── READY_teacher-time-saver.md          # Ready to post ✅
│   ├── READY_student-success-story.md       # Ready to post ✅
│   ├── POSTED_systems-thinking-tip.md       # Already posted
│   ├── 2025-11-17_facebook_systems-thinking-tip_v1.png
│   ├── 2025-11-20_facebook_teacher-tip_v1.png
│   └── 2025-11-21_facebook_success-story_v1.png
├── post_ready_files.py                      # Main script
└── SIMPLE-WORKFLOW.md                       # This file
```

---

## 🛠️ THE SCRIPT

**File**: `/workspace/repos/modelit-social-media-assets/post_ready_files.py`

```python
#!/usr/bin/env python3
"""
Simple script to post all READY_*.md files to Ayrshare
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
        with open(filepath, 'r') as f:
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
```

---

## ⚡ QUICK COMMANDS

### Post everything ready
```bash
cd /workspace/repos/modelit-social-media-assets
python post_ready_files.py
```

### Generate image for new post
```bash
python /workspace/scripts/generate_single_image.py "your prompt here"
```

### Check what's scheduled in Ayrshare
```bash
curl -X GET "https://api.ayrshare.com/api/history?action=scheduled" \
  -H "Authorization: Bearer 7D248853-8AF94A41-A48F07DC-73F74D88"
```

### Create new post from template
```bash
cd /workspace/repos/modelit-social-media-assets/facebook-posts
cat > READY_my-new-post.md << 'EOF'
---
status: READY
image: 2025-11-XX_facebook_topic_v1.png
---

Your post text here...

#Hashtags
EOF
```

---

## 📊 BATCH POSTING (Queue 10 Posts at Once)

**Workflow**:
1. Create 10 `READY_*.md` files in one sitting
2. Generate 10 images (or use stock photos)
3. Run `python post_ready_files.py` once
4. All 10 posts auto-scheduled every 2 days = 20 days of content ✅

**Time**: ~30 minutes to create 10 posts → 20 days of scheduled content

---

## 🔄 CONTINUOUS WORKFLOW

**Weekly routine**:
1. **Monday**: Create 3-4 new `READY_*.md` files
2. **Monday**: Generate images for new posts
3. **Monday**: Run `python post_ready_files.py`
4. **Done**: 6-8 days of content queued

**Monthly**: 4 weeks × 4 posts = 16 posts = 32 days of content

---

## 💡 PRO TIPS

### Tip 1: Draft posts anytime, post when ready
```bash
# Create draft
DRAFT_future-idea.md  # Ignored by script

# When ready, rename
READY_future-idea.md  # Script will post it
```

### Tip 2: Batch generate images
```bash
# Generate 5 images at once
for topic in "systems thinking" "teacher tips" "student success" "research" "accessibility"; do
    python /workspace/scripts/generate_single_image.py "Educational illustration for $topic"
done
```

### Tip 3: Preview before posting
```bash
# See what will be posted (without actually posting)
ls facebook-posts/READY_*.md
cat facebook-posts/READY_*.md  # Review content
```

### Tip 4: Re-post old content
```bash
# Rename POSTED back to READY
mv facebook-posts/POSTED_old-post.md facebook-posts/READY_old-post.md
python post_ready_files.py  # Will re-schedule
```

---

## ✅ ADVANTAGES OF THIS WORKFLOW

1. **Simple**: Just markdown files, no database or sheets
2. **Version controlled**: All posts in Git history
3. **Collaborative**: Team can create posts via GitHub web interface
4. **Visual**: See all posts in one folder
5. **Safe**: READY/POSTED prefixes prevent double-posting
6. **Flexible**: Create posts anywhere (web, mobile, IDE)

---

## 🎯 YOUR NEXT ACTION

**Create your next 5 posts**:
1. Copy-paste the markdown template 5 times
2. Fill in different content (one per content pillar)
3. Generate 5 images (or skip images for text-only posts)
4. Run `python post_ready_files.py`
5. Done! 10 days of scheduled content ✅

**Want me to create the script and example posts now?**
