# The Great Mo Showdown

Landing page for the Grow the Mo vs Mow the Mo Movember fundraiser.
A GitHub Action reads both Movember pages every 30 minutes and updates `data/totals.json`; the page reads that file and redraws the scoreboard.

## Set up (about 5 minutes)

1. **Create a public repository** on your personal GitHub account (for example `great-mo-showdown`) and upload everything in this folder, keeping the folder structure. GitHub Pages on a private repository needs a paid plan.
2. **Turn on GitHub Pages:** Settings → Pages → Source: *Deploy from a branch* → Branch: `main`, folder `/ (root)` → Save. Your page will be at `https://<your-username>.github.io/great-mo-showdown/`.
3. **Let the Action save totals:** Settings → Actions → General → Workflow permissions → *Read and write permissions* → Save.
4. **Run it once by hand:** Actions tab → *Update Mo totals* → *Run workflow*. Check the log shows a line like `grow: $0.00 (via text)` for each page.

After that it runs on its own every 30 minutes. It only commits when a total changes, and it stops updating once voting closes at 11:59 pm on 30 November (NZ time), so the result stays frozen.

## If a total can't be read

If Movember changes their page layout, the log will say `couldn't find the total on the page`, and a copy of the page is attached to that run as `movember-page-debug`. The scoreboard keeps showing the last good numbers in the meantime. To fix the numbers by hand, edit `data/totals.json` on GitHub.

## Files

- `index.html`: the page
- `data/totals.json`: current totals (written by the Action)
- `scripts/update_totals.py`: reads the Movember pages (no extra packages needed)
- `.github/workflows/update-totals.yml`: the 30-minute schedule
- `assets/`: animations, social preview image and the triangle motif

After the campaign, you can switch the schedule off under Actions → *Update Mo totals* → ⋯ → *Disable workflow*.
