---
trigger: always_on
description: "Enforce pushing all branches and tags exclusively to the user's panoptica GitHub mirror"
---

# Git Push Mirror Policy

- **Always Push to `panoptica` Mirror**: All `git push` operations in `/Users/mattmcconnon/gecx` MUST target `panoptica` (`https://github.com/panoptica/cxas-scrapi.git`), never upstream `https://github.com/GoogleCloudPlatform/cxas-scrapi.git`.
- **Verify Remote Config Before Pushing**: Ensure `remote.pushDefault=panoptica` and `remote.origin.pushurl=https://github.com/panoptica/cxas-scrapi.git` remain set when creating new branches or worktrees.
