"""
Step 2 Verification Script
Run this after installing dependencies to verify everything is set up correctly.

Usage:
    uv run python verify_setup.py
"""

import sys


def check_imports():
    """Check all required packages are importable."""
    results = []

    checks = [
        ("lightrag", "import lightrag"),
        ("ragas", "import ragas"),
        ("streamlit", "import streamlit"),
        ("pypdf", "from pypdf import PdfReader"),
        ("sentence-transformers", "from sentence_transformers import SentenceTransformer"),
        ("openai", "from openai import AsyncOpenAI"),
        ("python-dotenv", "from dotenv import load_dotenv"),
        ("plotly", "import plotly"),
        ("nest-asyncio", "import nest_asyncio"),
        ("numpy", "import numpy"),
    ]

    print("=" * 50)
    print("  Dependency Check")
    print("=" * 50)

    all_ok = True
    for name, import_stmt in checks:
        try:
            exec(import_stmt)
            status = "OK"
            icon = "✅"
        except ImportError as e:
            status = f"FAILED — {e}"
            icon = "❌"
            all_ok = False

        print(f"  {icon} {name:<25} {status}")

    print("=" * 50)

    if all_ok:
        print("  All imports successful. Ready for Step 3.")
    else:
        print("  Some imports failed. Fix them before proceeding.")
        sys.exit(1)


def check_config():
    """Check that app/config.py loads without errors."""
    print("\n" + "=" * 50)
    print("  Config Check")
    print("=" * 50)

    import os
    from pathlib import Path

    # Check .env.example exists
    if Path(".env.example").exists():
        print("  ✅ .env.example found")
    else:
        print("  ❌ .env.example missing")

    # Check .env exists
    if Path(".env").exists():
        print("  ✅ .env found")
    else:
        print("  ⚠️  .env not found — copy .env.example to .env and add your GROQ_API_KEY")

    # Check directory structure
    dirs = [
        "app",
        "app/ingestion",
        "app/rag",
        "app/evaluation",
        "app/ui",
        "data/papers",
        "eval_history",
        "tests",
    ]
    all_dirs_ok = True
    for d in dirs:
        if Path(d).exists():
            print(f"  ✅ {d}/")
        else:
            print(f"  ❌ {d}/ missing")
            all_dirs_ok = False

    # Check __init__.py files
    init_files = [
        "app/__init__.py",
        "app/ingestion/__init__.py",
        "app/rag/__init__.py",
        "app/evaluation/__init__.py",
        "app/ui/__init__.py",
    ]
    for f in init_files:
        if Path(f).exists():
            print(f"  ✅ {f}")
        else:
            print(f"  ❌ {f} missing")

    # Check config.py exists
    if Path("app/config.py").exists():
        print("  ✅ app/config.py found")
    else:
        print("  ❌ app/config.py missing")

    print("=" * 50)


if __name__ == "__main__":
    check_imports()
    check_config()