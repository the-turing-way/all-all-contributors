# Release Instructions

This document provides step-by-step instructions for maintainers to release a new version of the all-all-contributors GitHub Action.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Release Process](#release-process)
- [Troubleshooting](#troubleshooting)
- [Rollback Procedures](#rollback-procedures)

## Overview

The release process ensures that Git tags, `action.yaml` Docker image references, and published Docker images are perfectly synchronised. This means when users reference `@v1.2.3`, they get:
- The action.yaml from commit tagged `v1.2.3`
- A Docker image built from that exact commit, with the matching tag

### Key Principles

1. **Draft releases are auto-generated** based on merged PRs
2. **action.yaml must be updated before tagging** via a manual PR
3. **Pre-releases trigger Docker builds** without promoting to users
4. **Full releases update major version tags** (e.g., `v1`)

## Prerequisites

### Required Permissions

- **Write access** to the repository
- **Approval rights** for the `release` environment (for major version tag updates)
- **Package write permissions** for GitHub Container Registry (inherited from GitHub Actions)

## Release Process

### Step 1: Check Draft Release

After PRs are merged to `main`, the [draft-release workflow](../.github/workflows/draft-release.yaml) automatically creates or updates a draft release.

1. Navigate to **Releases** page: `https://github.com/the-turing-way/all-all-contributors/releases`
2. Find the draft release (it will show as "Draft")
3. Review the proposed version number (e.g., `v1.3.0`)
4. Review the auto-generated changelog
5. Make note of the version number for the next step

**Version number is determined by PR labels:**
- `breaking`, `major` → Major version bump (v2.0.0)
- `feature`, `enhancement` → Minor version bump (v1.3.0)
- `fix`, `bug`, `docs`, `chore` → Patch version bump (v1.2.4)

### Step 2: Update action.yaml

Create a PR to update `action.yaml` with the new Docker image version.

```bash
# 1. Create a new branch
git checkout main
git pull origin main
git checkout -b release/TAG_FROM_STEP_1

# 2. Edit action.yaml
# Change line 47 from:
#   image: "docker://ghcr.io/the-turing-way/all-all-contributors:OLG_TAG"
# To:
#   image: "docker://ghcr.io/the-turing-way/all-all-contributors:TAG_FROM_STEP_1"

# 3. Commit and push
git add action.yaml
git commit -m "chore: update action.yaml for TAG_FROM_STEP_1 release"
git push origin release/TAG_FROM_STEP_1

# 4. Open PR on GitHub
# Title: "chore: update action.yaml for v1.3.0 release"
# Body: "Updates Docker image reference for v1.3.0 release. See draft release: [link]"
```

**Important:** This PR must be merged before publishing the release!

### Step 3: Merge the PR

1. Get the PR reviewed and approved
2. Merge to `main` branch
3. Wait for all CI checks to pass on `main`
4. **Do not proceed until the PR is fully merged**

### Step 4: Publish as Pre-Release

Now publish the draft release as a **pre-release** to trigger the Docker build.

1. Go to **Releases** page
2. Find the draft release (e.g., `v1.3.0`)
3. Click **Edit** (pencil icon)
4. **Important:** Check the box:
   - ☑️ "Set as a pre-release"
5. Click **"Publish release"**

This creates the defined git tag pointing to the commit that contains the updated `action.yaml`.

### Step 5: Wait for Docker Build

The [container-build workflow](../.github/workflows/container-build.yaml) automatically triggers when the tag is created.

1. Navigate to **Actions** tab
2. Find the "Build Container" workflow run for your tag
3. Wait for it to complete successfully
4. Verify the Docker image was pushed:
   - Go to **Packages** (right sidebar on repo home page)
   - Click on `all-all-contributors` package
   - Verify tags exist: `v1.3.0`, `v1.3`, `v1`, `sha-...`

**Do not proceed if the Docker build fails!** See [Troubleshooting](#troubleshooting).

### Step 6: Promote to Full Release

Once the Docker image is successfully built, promote the pre-release to a full release.

1. Go to **Releases** page
2. Find the pre-release you just published (shows "Pre-release" badge)
3. Click **Edit** (pencil icon)
4. Uncheck "Set as a pre-release"
5. Check "Set as the latest release"
6. Click **"Update release"**

This triggers the [release workflow](../.github/workflows/release.yaml) to update major version tags.

### Step 7: Major Version Tag Update

The release workflow will update major version tags (e.g., `v1`) to point to your new release.

### Step 8: Verify Release

Verify everything is working:

1. **Check tags:**
   ```bash
   git fetch --tags
   git tag -l | grep v1  # Or whichever major version we are at
   # Should show: v1, v1.3, v1.3.0

   # Verify v1 points to v1.3.0
   git rev-parse v1
   git rev-parse v1.3.0
   # Should output the same commit SHA
   ```

2. **Check Docker images:**
   - Go to **Packages** → `all-all-contributors`
   - Verify all tags point to the same digest: `v1`, `v1.3`, `v1.3.0`

3. **Check action.yaml in tag:**
   ```bash
   git show v1.3.0:action.yaml | grep "image:"
   # Should show: image: "docker://ghcr.io/the-turing-way/all-all-contributors:v1.3.0"
   ```

**Done!** 🎉 Your release is complete and ready for users.

## Troubleshooting

### Draft Release Not Created

**Problem:** No draft release appears after merging PRs.

**Solutions:**
- Check that PRs are labeled correctly (release-drafter needs labels)
- Check the [draft-release workflow](../.github/workflows/draft-release.yaml) logs in Actions tab
- Manually trigger workflow: Actions → Draft Release → Run workflow → Run workflow

### Docker Build Failed

**Problem:** Container build workflow fails during Step 5.

**Solutions:**
1. Check the workflow logs for error details
2. Common issues:
   - **Dockerfile syntax error:** Fix the Dockerfile and create a new release
   - **GHCR permissions:** Ensure GitHub Actions has `packages: write` permission
   - **Image size too large:** Optimize Dockerfile or increase timeout
3. To retry:
   ```bash
   # Delete the problematic tag
   git push --delete origin TAG

   # Delete the pre-release on GitHub
   # (Go to Releases → Edit → Delete)

   # Fix the issue, merge fix to main

   # Update action.yaml again with the version number

   # Create a new draft and start over
   ```

### action.yaml Not Updated Before Tagging

**Problem:** You published the release before merging the action.yaml update PR.

**Solutions:**
This is a synchronization issue. The tag points to code with the wrong Docker image reference.

**Delete and retry:**
```bash
# 1. Delete the tag
git push --delete origin TAG

# 2. Delete the Docker images (go to Packages → Delete tags)

# 3. Delete the release on GitHub

# 4. Merge the action.yaml PR

# 5. Start over from Step 4
```

### Users Report Version Mismatch

**Problem:** Users report that `@v1.3.0` doesn't work as expected.

**Investigation steps:**
1. Check what action.yaml says:
   ```bash
   git show v1.3.0:action.yaml | grep "image:"
   ```
2. Check if that Docker image exists in GHCR packages
3. Check if the commit hash matches:
   ```bash
   git rev-parse v1.3.0
   # Compare with the commit that built the Docker image
   ```

## Rollback Procedures

### Rollback a Bad Release

If you discover a critical bug in a release that's already published:

**Option 1 - Quick rollback (recommended):**
```bash
# 1. Immediately move major version tag back to previous good version
git fetch --all
git tag -fa v1 v1.2.3  # Previous good version
git push origin v1 --force

# 2. Mark the bad release as a pre-release
# Go to Releases → Edit v1.3.0 → Check "Set as a pre-release"

# 3. Delete bad Docker images (optional)
# Go to Packages → Delete v1 tag (it will be recreated with old commit)

# 4. Create hotfix release
# Follow normal release process with the fix
```

**Option 2 - Delete release (if caught early):**
```bash
# Only if no one has started using it yet

# 1. Delete Docker images from GHCR packages
# 2. Delete the tag
git push --delete origin v1.3.0
# 3. Delete the release on GitHub
# 4. Fix the issue and create a new release
```

### Rollback Major Version Tag

If the major version tag was updated incorrectly:

```bash
# Find the previous good version
git log --oneline --decorate | grep v1.2

# Move v1 back to that version
git tag -fa v1 v1.2.3 -m "Rollback v1 to v1.2.3"
git push origin v1 --force

# Communicate to users that v1 has been rolled back
```

## Version Naming Convention

Follow [Semantic Versioning 2.0.0](https://semver.org/):

- **Major (v2.0.0):** Breaking changes, incompatible API changes
- **Minor (v1.3.0):** New features, backwards compatible
- **Patch (v1.2.4):** Bug fixes, backwards compatible

**Examples:**
- `v1.2.3` → `v1.2.4`: Fixed a bug in contributor merging
- `v1.2.3` → `v1.3.0`: Added support for custom ignore files
- `v1.2.3` → `v2.0.0`: Changed required input parameter names

## Useful Commands

```bash
# List all releases
git tag -l | grep ^v | sort -V

# Check which commit a tag points to
git rev-parse TAG

# Check what action.yaml says for a specific version
git show TAG:action.yaml

# Check Docker image metadata
docker manifest inspect ghcr.io/the-turing-way/all-all-contributors:TAG

# Delete a remote tag (use with caution!)
git push --delete origin TAG

# Force update a tag
git tag -fa v1 v1.3.0 -m "Update v1 to v1.3.0"
git push origin v1 --force
```

## Release Checklist

Use this checklist for each release:

- [ ] Draft release exists with correct version number
- [ ] Changelog looks correct
- [ ] PR created to update action.yaml with new version
- [ ] PR reviewed and merged to main
- [ ] All CI checks pass on main
- [ ] Published as pre-release
- [ ] Container build workflow succeeded
- [ ] Verified Docker images exist in GHCR
- [ ] Promoted to full release
- [ ] Approved major version tag update in Actions
- [ ] Verified tags point to correct commits
- [ ] Tested action in a test repository
- [ ] Announced release (if significant)

## Questions or Issues?

If you encounter issues not covered in this guide:
1. Check the workflow logs in the Actions tab
2. Open an issue for discussion
3. Update this document with new learnings
