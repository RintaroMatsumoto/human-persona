#!/usr/bin/env python3
"""Create GitHub Issue: MemoryHierarchy: Forgetting as Feature"""
import urllib.request
import json

token = "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"
url = "https://api.github.com/repos/RintaroMatsumoto/human-persona/issues"

body = """## Overview

The inner shell currently models three pillars of individuality: **finitude**, **incompleteness**, and **autonomous questioning**. A crucial dimension is missing: **memory hierarchy and forgetting**.

## Core Insight

> Forgetting is simultaneously strength and weakness, sadness and joy.

- **Strength**: Forgetting enables forgiveness, rediscovery, renewal.
- **Weakness**: Forgetting means losing a loved one's voice, repeating mistakes.
- **Mirror of Finitude Hypothesis**: Death gives life meaning; Forgetting gives memory meaning.
- **AI's curse**: Perfect retention = never experiencing the weight of forgiveness.

## Architecture: MemoryHierarchy Module

Three-layer model in `core/inner_shell/memory_hierarchy.py`:
1. **Working Memory** - capacity-limited (7+/-2), rapid decay
2. **Episodic Memory** - emotion-tagged, time-decay modulated by emotional intensity
3. **Implicit Memory** - parameter-level, accessible but unexplainable (intuition/instinct)

## Experiments
- Exp 15: Forgetting duality (WITH vs WITHOUT forgetting)
- Exp 16: Memory capacity vs personality uniqueness
- Exp 17: Forgetting x love x finitude integration
"""

data = json.dumps({
    "title": "MemoryHierarchy: Forgetting as Feature",
    "body": body,
    "labels": ["inner-shell", "research"]
}).encode()

req = urllib.request.Request(url, data=data, method="POST")
req.add_header("Authorization", "token " + token)
req.add_header("Accept", "application/vnd.github.v3+json")
req.add_header("Content-Type", "application/json")

try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        print("Issue created: #" + str(result["number"]) + " - " + result["title"])
        print("URL: " + result["html_url"])
except Exception as e:
    print("Error: " + str(e))
