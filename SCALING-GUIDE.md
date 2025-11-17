# 🚀 ModelIt Social Media Scaling Guide

**How to programmatically scale from 1 post to 100+ posts per month**

---

## 📍 WHERE POSTS ARE STORED

### 1. **Content Storage (GitHub)**
**Location**: `Alexandria-s-Design/modelit-social-media-assets`

```
modelit-social-media-assets/
├── facebook-posts/
│   ├── DRAFT_2025-11-17_systems-thinking-tip.md  # Content drafts
│   ├── 2025-11-17_facebook_systems-thinking-tip_v1.png  # Generated images
│   └── [future posts...]
├── instagram-stories/
├── linkedin-posts/
└── ai-generated/  # Raw AI-generated images before editing
```

**Why GitHub?**
- Version control for all content
- Raw URLs for Ayrshare `mediaUrls` parameter
- Collaborative editing (you can edit drafts via GitHub web interface)
- Automatic backup

**Access images programmatically**:
```python
image_url = f"https://raw.githubusercontent.com/Alexandria-s-Design/modelit-social-media-assets/main/facebook-posts/{filename}"
```

### 2. **Scheduled Posts (Ayrshare)**
**Location**: Ayrshare API (queryable via REST)

```bash
# Get all scheduled posts
curl -X GET "https://api.ayrshare.com/api/history?action=scheduled" \
  -H "Authorization: Bearer 7D248853-8AF94A41-A48F07DC-73F74D88"
```

**Returns**:
```json
{
  "posts": [
    {
      "id": "mFA0Uo6a5gcUWygZj0oe",
      "post": "Your content...",
      "status": "scheduled",
      "scheduleDate": "2025-11-19T15:00:00Z",
      "platforms": ["facebook"]
    }
  ]
}
```

### 3. **Published Posts (Facebook)**
**Location**: Facebook API (queryable via Ayrshare analytics)

```bash
# Get analytics for published post
curl -X GET "https://api.ayrshare.com/api/analytics/post?id=POST_ID&platforms=facebook" \
  -H "Authorization: Bearer 7D248853-8AF94A41-A48F07DC-73F74D88"
```

**Returns**: Likes, shares, comments, reach, impressions

---

## 📈 HOW TO SCALE PROGRAMMATICALLY

### **Level 1: Manual Batch (10-20 posts/month)**

**Workflow**: Pre-write content → Generate images → Batch schedule

**Script**: `/workspace/scripts/batch_schedule_facebook_posts.py`
```python
import requests
import json

API_KEY = "7D248853-8AF94A41-A48F07DC-73F74D88"
REPO_BASE = "https://raw.githubusercontent.com/Alexandria-s-Design/modelit-social-media-assets/main"

posts = [
    {
        "text": "🤔 Systems thinking tip #1...",
        "image": "2025-11-17_facebook_systems-thinking-tip_v1.png"
    },
    {
        "text": "👩‍🏫 Teacher empowerment tip...",
        "image": "2025-11-18_facebook_teacher-empowerment_v1.png"
    },
    # Add 10-20 posts here
]

for post in posts:
    response = requests.post(
        "https://api.ayrshare.com/api/post",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "post": post["text"],
            "platforms": ["facebook"],
            "mediaUrls": [f"{REPO_BASE}/facebook-posts/{post['image']}"],
            "autoSchedule": {"schedule": True, "title": "every_other_day"}
        }
    )
    print(f"✅ Scheduled: {response.json()['id']}")
```

**Run**:
```bash
python /workspace/scripts/batch_schedule_facebook_posts.py
```

Result: All posts queued to auto-schedule, no manual date calculation needed.

---

### **Level 2: Google Sheets Content Calendar (50+ posts/month)**

**Architecture**: Google Sheets → Python script → Ayrshare

**Setup**:
1. Create Google Sheet: "ModelIt Content Calendar"
2. Columns: `Date | Content Pillar | Post Text | Image Prompt | Status | Post ID`
3. Pre-fill 30-60 days of content ideas
4. Script reads sheet → generates images → schedules posts

**Script**: `/workspace/scripts/google_sheets_to_ayrshare.py`
```python
from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests

# Authenticate with Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
creds = service_account.Credentials.from_service_account_file(
    '/workspace/.credentials/google-sheets-service-account.json',
    scopes=SCOPES
)
service = build('sheets', 'v4', credentials=creds)

# Read content calendar
SPREADSHEET_ID = '1PY2tHFHr0gelLWC2SrCefW9EXi9CNrAdj8N1Vzc5u5s'
RANGE_NAME = 'ModelIt Content!A2:F100'  # Skip header row

result = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=RANGE_NAME
).execute()

rows = result.get('values', [])

for row in rows:
    if len(row) < 6 or row[4] == "Published":  # Skip if already published
        continue

    date, pillar, post_text, image_prompt, status, post_id = row

    # Generate image with Nano Banana
    image_response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer YOUR_OPENROUTER_API_KEY"
        },
        json={
            "model": "google/gemini-2.5-flash-image",
            "modalities": ["image", "text"],
            "messages": [{"role": "user", "content": image_prompt}]
        }
    )

    # Extract and save image (code from previous example)
    # ... save to GitHub repo with git commands

    # Schedule post to Ayrshare
    ayrshare_response = requests.post(
        "https://api.ayrshare.com/api/post",
        headers={"Authorization": "Bearer 7D248853-8AF94A41-A48F07DC-73F74D88"},
        json={
            "post": post_text,
            "platforms": ["facebook"],
            "mediaUrls": [f"https://raw.githubusercontent.com/.../image.png"],
            "autoSchedule": {"schedule": True, "title": "every_other_day"}
        }
    )

    # Update Google Sheet with Post ID
    post_id = ayrshare_response.json()['id']
    # ... update sheet row with post_id and status="Scheduled"

print("✅ All posts from calendar scheduled!")
```

**Benefits**:
- Collaborative content planning (you can edit sheet anywhere)
- Visual content calendar
- Track what's scheduled vs. published
- Easy to pause/resume campaigns

---

### **Level 3: AI Content Generation (100+ posts/month)**

**Architecture**: CrewAI agents → Generate content → Nano Banana → Ayrshare

**Workflow**:
1. **Content Agent**: Generates 30 days of post ideas based on content pillars
2. **Image Agent**: Creates image prompts for each post
3. **Generation Loop**: Nano Banana generates images ($0.039 each)
4. **Scheduling Agent**: Batches posts to Ayrshare auto-schedule

**Script**: `/workspace/scripts/ai_content_empire.py`
```python
from crewai import Agent, Task, Crew
import requests
import json

# Define AI agents
content_writer = Agent(
    role="Social Media Content Writer",
    goal="Generate engaging Facebook posts about ModelIt K12",
    backstory="Expert in educational technology and social media engagement",
    llm="anthropic/claude-3.5-sonnet"  # Via OpenRouter
)

image_prompter = Agent(
    role="Visual Content Designer",
    goal="Create detailed image prompts for educational illustrations",
    backstory="Expert in visual storytelling for STEM education"
)

# Task: Generate 30 posts
generate_posts_task = Task(
    description="""
    Generate 30 Facebook posts for ModelIt K12 following this pattern:
    - 6 posts per content pillar (Systems Thinking, Teacher Empowerment, Real-World Impact, etc.)
    - Each post: engaging hook, educational value, call-to-action
    - Include relevant hashtags
    - Output as JSON array
    """,
    agent=content_writer
)

generate_images_task = Task(
    description="""
    For each of the 30 posts, create a detailed image prompt suitable for
    Gemini 2.5 Flash Image generation. Focus on clean, modern, educational aesthetics.
    Output as JSON array matching posts.
    """,
    agent=image_prompter
)

# Run crew
crew = Crew(agents=[content_writer, image_prompter], tasks=[generate_posts_task, generate_images_task])
result = crew.kickoff()

posts = json.loads(result)

# Generate images and schedule posts
for i, post in enumerate(posts):
    # Generate image
    image_response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": "Bearer YOUR_OPENROUTER_API_KEY"},
        json={
            "model": "google/gemini-2.5-flash-image",
            "modalities": ["image", "text"],
            "messages": [{"role": "user", "content": post['image_prompt']}]
        }
    )

    # Save image to GitHub (via git commands)
    # ... (code from previous example)

    # Schedule to Ayrshare
    ayrshare_response = requests.post(
        "https://api.ayrshare.com/api/post",
        headers={"Authorization": "Bearer 7D248853-8AF94A41-A48F07DC-73F74D88"},
        json={
            "post": post['text'],
            "platforms": ["facebook"],
            "mediaUrls": [f"https://raw.githubusercontent.com/.../image_{i}.png"],
            "autoSchedule": {"schedule": True, "title": "every_other_day"}
        }
    )

    print(f"✅ Post {i+1}/30 scheduled: {ayrshare_response.json()['id']}")

print("🎉 30-day content calendar fully automated!")
```

**Cost**: 30 images × $0.039 = **$1.17 for 30 days of content**

---

### **Level 4: Autonomous Content Empire (Unlimited)**

**Architecture**: Scheduled workflows → Auto-generation → Auto-posting

**Tools**:
- **n8n workflow**: Runs daily at 8am
- **CrewAI research agent**: Finds trending topics in STEM education
- **Content generation**: Creates post + image prompt
- **Nano Banana**: Generates image
- **Ayrshare**: Auto-schedules post

**n8n Workflow Structure**:
```
[Schedule Trigger: Daily 8am]
    ↓
[HTTP Request: OpenRouter API]
    → Prompt: "Generate engaging Facebook post about [trending_topic] for ModelIt K12"
    ↓
[HTTP Request: Gemini 2.5 Flash Image]
    → Generate image from AI-created prompt
    ↓
[Code Node: Save to GitHub]
    → Commit image to modelit-social-media-assets repo
    ↓
[HTTP Request: Ayrshare API]
    → Schedule post with autoSchedule
    ↓
[Google Sheets: Log Post]
    → Record post ID, date, topic, performance
```

**Setup**:
1. Create n8n workflow (access via `http://localhost:5678`)
2. Configure schedule trigger
3. Test workflow manually
4. Activate for autonomous daily posting

**Result**: Zero manual work, infinite content pipeline

---

## 📊 SCALING ECONOMICS

| Method | Posts/Month | Time Investment | Cost | Best For |
|--------|-------------|-----------------|------|----------|
| **Manual** | 10-20 | 2 hours/week | $0.78-$1.56 | Testing, learning |
| **Batch** | 30-50 | 4 hours/month | $1.17-$1.95 | Established strategy |
| **Sheets** | 50-100 | 8 hours setup, 1 hour/month | $1.95-$3.90 | Team collaboration |
| **AI Auto** | 100-1000 | 16 hours setup, 0 hours/month | $3.90-$39.00 | Scale business |

**Your Quota**: 1,000 posts/month (Ayrshare Business Plan)

---

## 🔧 QUICK START: NEXT 10 POSTS

Want to queue your next 10 posts right now? Here's the fastest path:

**1. Create a simple JSON file**:
```json
{
  "posts": [
    {"pillar": "Systems Thinking", "topic": "feedback loops"},
    {"pillar": "Teacher Empowerment", "topic": "no-prep lessons"},
    {"pillar": "Real-World Impact", "topic": "STEM careers"},
    {"pillar": "Research-Backed", "topic": "Cell Collective partnership"},
    {"pillar": "Reaching Every Learner", "topic": "accessibility features"},
    {"pillar": "Systems Thinking", "topic": "cause-effect relationships"},
    {"pillar": "Teacher Empowerment", "topic": "time-saving tips"},
    {"pillar": "Real-World Impact", "topic": "student success stories"},
    {"pillar": "Research-Backed", "topic": "published research"},
    {"pillar": "Reaching Every Learner", "topic": "diverse learners"}
  ]
}
```

**2. Run the generator**:
```bash
python /workspace/scripts/generate_next_10_posts.py
```

**3. Review drafts in GitHub repo**:
```bash
# Opens GitHub repo in browser
start https://github.com/Alexandria-s-Design/modelit-social-media-assets/tree/main/facebook-posts
```

**4. Batch schedule**:
```bash
python /workspace/scripts/batch_schedule_facebook_posts.py
```

**Done!** 10 posts queued, images generated, auto-scheduled every 2 days = 20 days of content.

---

## 📚 RELATED DOCUMENTATION

- **Ayrshare Setup**: `/workspace/docs/AYRSHARE-SETUP-COMPLETE.md`
- **Nano Banana Guide**: `/workspace/docs/NANO-BANANA-GUIDE.md`
- **CrewAI Guide**: `/workspace/docs/CREWAI-GUIDE.md`
- **n8n Workflows**: `/workspace/docs/N8N-PROGRAMMATIC-CONTROL-GUIDE.md`

---

**Questions?** Ask Claude to create any of these scripts or workflows!
