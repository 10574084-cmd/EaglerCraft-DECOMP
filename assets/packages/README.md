# Eaglercraft 26.3 separated resources

The resource packs are separated into five ZIP uploads so each file stays below GitHub's browser upload size limit.

## Upload these five files into this folder

- `vibe26-images.zip` — 3,973 PNG images.
- `vibe26-json.zip` — 15,704 JSON data files.
- `vibe26-engine-data.zip` — 1,823 NBT, shader, metadata and other engine-data files.
- `vibe26-audio-part1.zip` — 2,389 OGG audio files.
- `vibe26-audio-part2.zip` — 2,390 OGG audio files.

The audio package is split into two parts because the complete sound archive is larger than GitHub's browser uploader limit.

## Import into the repository

1. Download the five ZIP files from the links in the ChatGPT conversation.
2. Open this folder in the GitHub repository: `assets/packages/`.
3. Upload all five ZIP files and commit them to `main`.
4. Open **Actions → Import Eaglercraft Resource Packages → Run workflow**.
5. The workflow verifies the ZIPs, checks their expected file counts and extensions, safely extracts them, and commits the separate folders.

The resulting layout is:

```text
assets/
  images/       # PNG textures and images
  json/         # JSON assets and engine data
  data/         # NBT, shaders, mcmeta and remaining files
  audio/        # OGG sounds
  packages/     # upload instructions and manifest
```

The workflow removes the uploaded ZIPs after successful extraction. It does not alter the VIBE client or the original HTML build.
