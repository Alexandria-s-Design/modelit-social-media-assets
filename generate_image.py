#!/usr/bin/env python3
"""
Generate a single image with Nano Banana (Gemini 2.5 Flash Image)
Usage: python generate_image.py "your image prompt here"
"""
import sys
import os
import requests
import base64
from datetime import datetime

# Configuration - Load from environment to avoid exposing keys
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    # Fallback: Try loading from /workspace/.env
    env_path = '/workspace/.env'
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith('OPENROUTER_API_KEY='):
                    OPENROUTER_API_KEY = line.split('=', 1)[1].strip()
                    break

if not OPENROUTER_API_KEY:
    print("❌ Error: OPENROUTER_API_KEY not found in environment or /workspace/.env")
    sys.exit(1)

def generate_image(prompt, topic_slug):
    """Generate image with Gemini 2.5 Flash Image"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "google/gemini-2.5-flash-image",
            "modalities": ["image", "text"],
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
    )

    if response.status_code == 200:
        data = response.json()

        # Extract image from response
        message = data['choices'][0]['message']

        if 'images' in message and len(message['images']) > 0:
            # Get first image
            image_obj = message['images'][0]
            image_url = image_obj['image_url']['url']

            # Extract base64 data (format: data:image/png;base64,...)
            if ',' in image_url:
                image_data = image_url.split(',')[1]
            else:
                image_data = image_url

            # Generate filename
            date_str = datetime.now().strftime('%Y-%m-%d')
            filename = f"{date_str}_facebook_{topic_slug}_v1.png"
            output_path = f"facebook-posts/{filename}"

            # Save image
            with open(output_path, 'wb') as f:
                f.write(base64.b64decode(image_data))

            print(f"✅ Image generated successfully!")
            print(f"📁 Saved to: {output_path}")
            print(f"💰 Cost: ~$0.039")
            print(f"\n📋 Add this to your markdown frontmatter:")
            print(f"image: {filename}")

            return filename
        else:
            print("❌ No images found in response")
            return None
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_image.py \"your image prompt\" [topic-slug]")
        print("\nExample:")
        print('python generate_image.py "Educational illustration showing systems thinking" "systems-thinking"')
        sys.exit(1)

    prompt = sys.argv[1]
    topic_slug = sys.argv[2] if len(sys.argv) > 2 else "post"

    # Enhance prompt with ModelIt style guidelines
    enhanced_prompt = f"""{prompt}

Style guidelines:
- Modern, clean, professional aesthetic
- Warm, inviting colors (blues, greens, oranges)
- Suitable for middle/high school science education
- No text in the image
- Focus on visual storytelling and education"""

    print(f"🎨 Generating image for: {topic_slug}")
    print(f"💭 Prompt: {prompt}\n")

    generate_image(enhanced_prompt, topic_slug)

if __name__ == "__main__":
    main()
