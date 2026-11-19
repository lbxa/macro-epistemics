# Video production uses Community Manim and the frozen pilot

- **Date:** 2026-11-16
- **Status:** Accepted
- **Deciders:** Lucas Barbosa
- **Area:** report/video

## Context

Lucas approved the Macro-Epistemics storyboard, authorized production of a first
draft under two minutes, and explicitly requested Manim Community. He designated
the ignored root `video/` directory for production files and large assets.
Broader sector experiments are still developing alongside this work.

## Decision

Produce the 118-second film with Manim Community 0.22.1 in a separate environment
inside `video/`. Keep animation source, narration, original music, caches,
previews, exports and evidence copies there. Use the frozen legal pilot admitted
by [the storyboard](../../report/epistemics/storyboard.md); label the broader
study as research direction and the human applications as vision.

## Consequences

The movie can be revised without modifying the experiment harness or its locked
environment. Production files are deliberately absent from Git, so a checkout
alone cannot recover the video; retain the local production folder separately.
Narration uses native Cloudflare TTS with a separate US$2 ceiling and cached
clips. The score is composed locally and rendered offline from a licensed
SoundFont. No new model-behavior experiment or public upload is part of this
production authorization.
