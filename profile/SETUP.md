# How to publish the profile README

`README.md` in this folder is written for your **GitHub profile page** — the panel that appears at the top of https://github.com/limamarcelinog.

GitHub shows it only if it lives in a public repository named exactly like your username. That repository does not exist yet.

## Steps

1. Go to https://github.com/new
2. **Repository name:** `limamarcelinog` — exactly your username. GitHub will show a note saying you found a secret: that is the confirmation you typed it right.
3. Set it to **Public**, tick **Add a README file**, and create it.
4. Copy the contents of [README.md](README.md) from this folder into that repository's `README.md` and commit.

Or from the terminal:

```bash
git clone git@github.com:limamarcelinog/limamarcelinog.git
cp profile/README.md limamarcelinog/README.md
cd limamarcelinog && git add README.md && git commit -m "profile" && git push
```

(The repository still has to be created on github.com first — step 2.)

## Keep it in sync

This folder is the source. When you change the profile text, change it here and copy it over, so the two do not drift apart.
