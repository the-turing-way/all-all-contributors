# Repository Setup Guide

This guide walks through the one-time configuration needed to enable the automated release workflow for all-all-contributors.

## Overview

Before you can use the release workflows, the GitHub repository must be configured with:
1. GitHub Container Registry (GHCR) enabled
2. Release environment with approvers
3. Branch protection rules (recommended)
4. Proper repository permissions

**Time required:** ~15 minutes
**Who can do this:** Repository administrators

## Prerequisites

- Admin access to the `the-turing-way/all-all-contributors` repository
- At least one other maintainer to act as release approver

## 1. Enable GitHub Container Registry

GHCR should already be enabled, but verify:

### Verify GHCR is Working

1. Go to the repository home page
2. Look for **Packages** in the right sidebar
3. You should see the `all-all-contributors` package listed

If you don't see it:
1. Push a commit to trigger the `container-build.yaml` workflow
2. The workflow will create the package automatically
3. Check **Actions** tab to verify the workflow succeeded

### Configure Package Visibility

1. Click on the `all-all-contributors` package
2. Click **Package settings** (gear icon)
3. Scroll to **Danger Zone**
4. Verify **Visibility** is set to **Public**
5. If not, click **Change visibility** → **Public** → Confirm

### Link Package to Repository

1. Still in **Package settings**
2. Scroll to **Connect repository**
3. If not already connected, click **Connect repository**
4. Select `the-turing-way/all-all-contributors`
5. Click **Connect**

## 2. Create Release Environment

The release environment provides a manual approval gate for updating major version tags.

### Step 1: Navigate to Environments

1. Go to repository **Settings**
2. In the left sidebar, click **Environments**
3. Click **New environment**

### Step 2: Create Environment

1. **Name:** `release` (must be exactly this name)
2. Click **Configure environment**

### Step 3: Configure Environment Protection Rules

On the environment configuration page:

#### Enable Deployment Protection Rules

Check the box: **☑️ Required reviewers**

#### Add Reviewers

1. Click **Add reviewers**
2. Add at least 1-2 maintainers who can approve releases
3. Recommended: Add 2+ people for redundancy
4. Click **Save protection rules**

**Suggested reviewers:**
- Repository owners
- Senior maintainers
- People who understand the release process

#### Optional: Deployment Branches

You can restrict which branches can trigger deployments:

1. Under **Deployment branches**, select **Selected branches**
2. Click **Add deployment branch rule**
3. Enter `main` as the branch name pattern
4. Click **Add rule**

This ensures only releases from `main` can update version tags.

### Step 4: Verify Configuration

Your environment should show:
- ✅ **Required reviewers:** [list of reviewers]
- ✅ **Deployment branches:** Only `main` (optional)

## 3. Configure Branch Protection (Recommended)

Protect the `main` branch to prevent accidental changes and ensure code quality.

### Step 1: Navigate to Branch Settings

1. Go to repository **Settings**
2. Click **Branches** in left sidebar
3. Under **Branch protection rules**, click **Add rule**

### Step 2: Configure Protection Rule

**Branch name pattern:** `main`

**Recommended settings:**

☑️ **Require a pull request before merging**
- ☑️ Require approvals: **1**
- ☑️ Dismiss stale pull request approvals when new commits are pushed
- ☑️ Require review from Code Owners (if you have CODEOWNERS file)

☑️ **Require status checks to pass before merging**
- ☑️ Require branches to be up to date before merging
- **Select required checks:**
  - `test` (from test.yaml workflow)
  - `build` (from container-build.yaml workflow)
  - `build_docs` (from build-docs.yml workflow)

☑️ **Require conversation resolution before merging**

☑️ **Include administrators** (recommended for consistency)

**Optional:**
- ☑️ Require signed commits
- ☑️ Require linear history

### Step 3: Save Changes

Click **Create** at the bottom of the page.

## 4. Verify Repository Permissions

Ensure GitHub Actions has the necessary permissions.

### Step 1: Navigate to Actions Settings

1. Go to repository **Settings**
2. Click **Actions** → **General** in left sidebar
3. Scroll to **Workflow permissions**

### Step 2: Configure Permissions

Select: **Read and write permissions**

This allows workflows to:
- Push Docker images to GHCR
- Create and update Git tags
- Update releases

**Alternative (more restrictive):**
If you prefer **Read repository contents and packages permissions**, you must add explicit permissions to each workflow file. The current workflows already include necessary `permissions:` blocks.

### Step 3: Additional Settings

In the same page:

☑️ **Allow GitHub Actions to create and approve pull requests**

This is needed if the draft-release workflow creates PRs (currently it doesn't, but good to enable for future use).

## 5. Verify Everything Works

Test the complete setup before your first release.

### Test 1: Draft Release Workflow

1. Create a test PR with a `feature` label
2. Merge the PR to `main`
3. Go to **Actions** tab
4. Verify **Draft Release** workflow runs successfully
5. Go to **Releases** tab
6. Verify a draft release was created or updated

### Test 2: Container Build Workflow

1. Go to **Actions** tab
2. Find a recent **Build Container** workflow run
3. Verify it succeeded
4. Go to **Packages**
5. Verify Docker image was pushed with appropriate tags

### Test 3: Release Environment

1. Go to **Settings** → **Environments** → **release**
2. Verify reviewers are listed
3. Make a note of who can approve releases

## 6. First Release Setup

Before making your first release with the new workflow:

### Update action.yaml for Initial Release

The current `action.yaml` references a hardcoded image. You need to establish a baseline version.

**Option A: Start with v1.0.0**

1. Create PR to update action.yaml to reference `v1.0.0`
2. Merge the PR
3. Follow the [Release Instructions](RELEASE.md) to create v1.0.0
4. This becomes your baseline version

**Option B: Use current state as v0.1.0**

If you're not ready for v1.0.0:

1. Create PR to update action.yaml to reference `v0.1.0`
2. Merge the PR
3. Follow the [Release Instructions](RELEASE.md) to create v0.1.0
4. Future releases can be v0.2.0, v0.3.0, etc. until ready for v1.0.0

### Recommended Approach

Start with **v1.0.0** since:
- The action is already functional and used in production
- Contributor table generation is a new feature, not a breaking change
- Users expect stability from v1.x releases

## Configuration Checklist

Use this checklist to verify setup is complete:

- [ ] GHCR package exists and is public
- [ ] GHCR package is linked to repository
- [ ] `release` environment created
- [ ] At least 1 reviewer added to `release` environment
- [ ] Branch protection enabled on `main` (optional but recommended)
- [ ] Required status checks configured (optional but recommended)
- [ ] GitHub Actions has read/write permissions
- [ ] Draft release workflow tested
- [ ] Container build workflow verified working
- [ ] Release environment access verified
- [ ] Initial version tag decided (v1.0.0 or v0.1.0)
- [ ] Team briefed on release process

## Troubleshooting

### Can't Create Environment

**Issue:** "Environments" option not visible in Settings.

**Solution:** Environments are available in:
- Public repositories (any plan)
- Private repositories (GitHub Pro, Team, or Enterprise)

If using a private repo on Free plan, you'll need to upgrade or make the repo public.

### Workflow Fails with "Resource not accessible by integration"

**Issue:** Workflow fails when trying to push images or update tags.

**Solution:**
1. Check **Settings** → **Actions** → **General** → **Workflow permissions**
2. Ensure **Read and write permissions** is selected
3. Or verify individual workflow files have appropriate `permissions:` blocks

### Can't Add Reviewers to Environment

**Issue:** People you want to add aren't available in the dropdown.

**Solution:**
- Users must have **Write access** or higher to the repository
- Go to **Settings** → **Collaborators** to add them first
- Then retry adding them as environment reviewers

### Draft Release Not Created

**Issue:** Draft release workflow runs but no draft appears.

**Solution:**
1. Check workflow logs for errors
2. Verify PRs have appropriate labels (`feature`, `fix`, etc.)
3. Check that `release-drafter.yml` config file exists
4. Try manually triggering the workflow:
   - Go to **Actions** tab
   - Click **Draft Release** workflow
   - Click **Run workflow** → **Run workflow**

## Next Steps

After completing this setup:

1. Review the [Release Instructions](RELEASE.md)
2. Brief the team on the release process
3. Create your first release following the documented process
4. Update this guide if you encounter any issues or have improvements

## Questions?

If you encounter issues not covered here:
1. Check the workflow logs in the **Actions** tab
2. Review the [Release Instructions](RELEASE.md) for runtime issues
3. Consult the [spec document](../.claude/spec/automated-release-workflow.md) for design decisions
4. Open an issue for discussion
