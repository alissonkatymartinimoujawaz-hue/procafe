# -*- coding: utf-8 -*-
"""Rebuild every output: clean tables, metrics, charts, PowerPoint deck and Word guide.

    python research/coffee-demand/scripts/build_all.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import analysis      # noqa: E402
import build_deck    # noqa: E402
import build_doc     # noqa: E402

if __name__ == "__main__":
    analysis.build(save=True)
    build_deck.build()
    build_doc.build()
