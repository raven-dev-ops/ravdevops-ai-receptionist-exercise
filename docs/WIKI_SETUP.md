# Wiki Setup

Source pages for the GitHub wiki are included in the `wiki/` directory.

## Wiki Publication Tasklist

- [ ] Enable Wiki in repository settings.
- [ ] Choose either the manual method or the git method below.
- [ ] Publish pages in the recommended order after copying the source markdown.

## Manual Method

- [ ] Open the Wiki tab in GitHub.
- [ ] Create pages matching the files in `wiki/`.
- [ ] Copy the markdown content from each source file.

## Git Method

GitHub wikis are separate repositories named like:

```text
<repo-name>.wiki.git
```

Example flow:

```bash
git clone git@github.com:<org-or-user>/<repo-name>.wiki.git
cp ../ravdevops-ai-receptionist-exercise/wiki/*.md <repo-name>.wiki/
git add .
git commit -m "Initialize exercise wiki"
git push
```

## Recommended Page Order

- [ ] Home
- [ ] Candidate Handbook
- [ ] Exercise Architecture
- [ ] Maintainer Workflow
- [ ] FAQ
