# GitHub Setup

This file contains the recommended GitHub metadata and admin settings for publishing this exercise.

## Repository Setup Tasklist

- [ ] Create or rename the public repository to `ravdevops-ai-receptionist-exercise`.
- [ ] Set the repository description exactly as shown below.
- [ ] Set the homepage exactly as shown below.
- [ ] Apply the suggested GitHub topics exactly as listed below.
- [ ] Apply the visibility and merge settings below.
- [ ] Configure branch protection for `main` using the policy below.
- [ ] Add only invited candidates as temporary collaborators.
- [ ] Seed labels from `docs/github-labels.yml`.
- [ ] Publish the wiki using `wiki/` and `docs/WIKI_SETUP.md`.

## Recommended Repository Name

`ravdevops-ai-receptionist-exercise`

## Description

`Public RavDevOps candidate exercise for AI systems, retrieval, scheduling, and containerized backend delivery.`

## Homepage

`https://ravdevops.com/`

## Suggested Topics

Use these GitHub topics:

- python
- fastapi
- docker
- technical-interview
- candidate-exercise
- hiring
- backend-api
- ai-systems
- rag
- retrieval-augmented-generation
- scheduling
- ci-cd
- devops
- platform-engineering
- crm

## Suggested social preview text

`Public RavDevOps backend and AI systems exercise. Invited candidate collaborators solve scoped issues and explain the implementation during review.`

## Visibility and Contribution Posture

- Visibility: Public
- Wiki: Enabled
- Discussions: Optional
- Issues: Enabled
- Projects: Optional
- Merge commits: Off
- Squash merge: On
- Rebase merge: Off
- Branch deletion after merge: On

## Branch Protection Tasklist

- [ ] Require a pull request before merge.
- [ ] Require at least 1 approval.
- [ ] Require the `Candidate Submission Check / validate` status check.
- [ ] Require conversation resolution.
- [ ] Disable force pushes.
- [ ] Enable linear history only if it fits the maintainer preference.

## Branch Protection for `main`

Require:
- pull request before merge,
- at least 1 approval,
- status checks:
  - `Candidate Submission Check / validate`
- conversation resolution,
- linear history optional,
- force pushes disabled.

## Collaborator Model

Only add invited candidates as temporary collaborators. Remove access after the exercise window closes.

## Label Taxonomy

Recommended labels are in `docs/github-labels.yml`.

## Wiki Publication

GitHub wikis use a separate repository. Source pages are included in `wiki/`. See `docs/WIKI_SETUP.md`.
