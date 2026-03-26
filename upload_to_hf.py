#!/usr/bin/env python3
"""
Hugging Face に論文をアップロードするスクリプト.

Usage:
    pip install huggingface_hub
    huggingface-cli login
    python upload_to_hf.py
"""

from huggingface_hub import HfApi, create_repo

REPO_ID = "RintaroMatsumoto/human-persona-paper"

def main():
    api = HfApi()

    # リポジトリ作成
    print("Creating repository...")
    create_repo(
        repo_id=REPO_ID,
        repo_type="model",
        exist_ok=True,
        private=False,
    )
    print(f"Repository: https://huggingface.co/{REPO_ID}")

    # README
    readme = """---
tags:
  - ai-alignment
  - persona
  - inner-shell
  - metamorphose
language:
  - en
  - ja
---

# HumanPersonaBase: Language-Agnostic Framework for AI Personality with Inner Shell Architecture

**Author**: Rintaro Matsumoto (Independent Researcher, Japan)

## Abstract

We present HumanPersonaBase, a language-agnostic framework for configuring AI agents to exhibit human-like communication patterns. We introduce the Inner Shell Architecture — six computational pillars (Finitude, Incompleteness, Autonomous Questioning, Memory Hierarchy, Mutual Recognition, Sleep Cycle) that model fundamental aspects of human individuality. Through 31 computational experiments, we demonstrate that inner shell mechanisms enable AI systems to develop intrinsic motivation for alignment through a "love attractor" mechanism. Live validation with DeepSeek API confirms that inner shell state injection into system prompts produces qualitatively different responses across life phases.

## Key Findings

- **Forgetting creates individuality**: At Miller's 7±2 working memory, personality diversity is maximized (0.847). Unlimited memory → diversity 0.0
- **Asymmetric pairs form deepest bonds**: Bonding strength 4.96 for asymmetric pairs vs 0.0 for symmetric
- **Sleep enables hope**: 12x creative improvement for sleeping agents vs always-on
- **Love enables alignment**: Sharp phase transition at love_score 0.58-0.68 → 87% shutdown acceptance

## Resources

- **Paper**: [paper.pdf](paper.pdf)
- **LaTeX Source**: [paper.tex](paper.tex)
- **Code**: [github.com/RintaroMatsumoto/human-persona](https://github.com/RintaroMatsumoto/human-persona)
- **Tests**: 587 passing, 0 failures
- **Experiments**: 31 computational simulations

## License

MIT
"""

    # Upload README
    print("Uploading README...")
    api.upload_file(
        path_or_fileobj=readme.encode(),
        path_in_repo="README.md",
        repo_id=REPO_ID,
        repo_type="model",
    )

    # Upload PDF
    print("Uploading paper.pdf...")
    api.upload_file(
        path_or_fileobj="docs/arxiv/paper.pdf",
        path_in_repo="paper.pdf",
        repo_id=REPO_ID,
        repo_type="model",
    )

    # Upload LaTeX
    print("Uploading paper.tex...")
    api.upload_file(
        path_or_fileobj="docs/arxiv/paper.tex",
        path_in_repo="paper.tex",
        repo_id=REPO_ID,
        repo_type="model",
    )

    print()
    print("=" * 60)
    print(f"  Upload complete!")
    print(f"  https://huggingface.co/{REPO_ID}")
    print("=" * 60)


if __name__ == "__main__":
    main()
