#!/usr/bin/env python3
"""Quick test script for Red Hat Corporate Vertex AI endpoint integration."""

import asyncio
import os
import sys

import httpx


async def test_corporate_endpoint():
    """Test basic connectivity to the corporate endpoint."""

    # Check environment variables
    model_api = os.environ.get("MODEL_API")
    user_key = os.environ.get("USER_KEY")
    model_id = os.environ.get("MODEL_ID", "claude-haiku-4-5@20251001")

    if not model_api:
        print("❌ ERROR: MODEL_API environment variable not set")
        print("   Set it with: export MODEL_API='https://claude--apicast-production.apps.int.stc.ai.prod.us-east-1.aws.paas.redhat.com:443'")
        return False

    if not user_key:
        print("❌ ERROR: USER_KEY environment variable not set")
        print("   Set it with: export USER_KEY='your-credential-here'")
        return False

    print("✅ Environment variables found:")
    print(f"   MODEL_API: {model_api}")
    print(f"   MODEL_ID: {model_id}")
    print(f"   USER_KEY: {'*' * 20}{user_key[-4:]}")
    print()

    # Determine model tier
    model_tier = "haiku"
    if "sonnet" in model_id.lower():
        model_tier = "sonnet"
    elif "opus" in model_id.lower():
        model_tier = "opus"

    url = f"{model_api}/{model_tier}/models/{model_id}:streamRawPredict"

    # Simple test request
    payload = {
        "anthropic_version": "vertex-2023-10-16",
        "max_tokens": 50,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": "Say 'test successful' if you can read this."}]
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {user_key}",
        "Content-Type": "application/json",
    }

    print(f"🔄 Testing connection to: {url}")
    print()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                text = ""
                for block in content:
                    if block.get("type") == "text":
                        text += block.get("text", "")

                usage = data.get("usage", {})

                print("✅ SUCCESS! Connection established.")
                print()
                print(f"Response: {text}")
                print()
                print(f"Token usage:")
                print(f"  Input:  {usage.get('input_tokens', 0)} tokens")
                print(f"  Output: {usage.get('output_tokens', 0)} tokens")
                print()
                print("🎉 Your corporate endpoint is ready to use!")
                print()
                print("Next steps:")
                print("  1. Copy the config: cp config.corp.yaml config.yaml")
                print("  2. Run a test: meta-eval evaluate --sample-size 10")
                return True
            else:
                print(f"❌ ERROR: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                return False

    except httpx.TimeoutException:
        print("❌ ERROR: Connection timeout")
        print("   - Check that you're connected to Red Hat VPN")
        print("   - Verify the MODEL_API URL is correct")
        return False
    except httpx.ConnectError as e:
        print(f"❌ ERROR: Connection failed: {e}")
        print("   - Check that you're connected to Red Hat VPN")
        print("   - Verify the MODEL_API URL is correct")
        return False
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_corporate_endpoint())
    sys.exit(0 if success else 1)
