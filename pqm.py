#!/usr/bin/env python3

import sentry_sdk
import src.main

"""
sentry_sdk.init(
    "https://7103b46a26394672a778debc94e11a81@o468780.ingest.sentry.io/5497332",
    traces_sample_rate=1.0)
"""

src.main.main()
