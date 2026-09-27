# Promo copy (drafts)

Drafts for sharing Courtside Analytics. **Nothing here has been posted anywhere.** Edit freely before using any of it. All figures match the live site as of September 2026.

Links:
- Live: https://betting-dashboard.onrender.com
- Code: https://github.com/Konstantinos-Sakellariou/betting-dashboard
- Social preview image (used automatically when the live link is pasted): `src/betting_dashboard/assets/og-image.png`
- Demo GIF: `docs/demo.gif`

---

## LinkedIn post

About 1,450 characters (LinkedIn allows 3,000, but only the first two lines show before "see more", so the hook comes first). Paste the live link last, so LinkedIn builds the preview card from it. You can attach `docs/demo.gif` as well; LinkedIn plays GIFs in the feed.

> I revived an old side project: a model that predicted European and NBA basketball scores, and a dashboard that grades every pick it ever published.
>
> When I reopened it, it didn't even start: the data had been deleted from the repo. Rebuilding it taught me more than building it did:
>
> 🔎 I recovered the data from git history and found a date bug that had put 18% of the European games in the wrong season.
> 📉 I stopped trusting accuracy. The model picked 67.6% of winners and still lost money, because favourites pay so little.
> 🎯 One strategy held up: betting totals only when the model disagreed with the bookmaker by more than 2.5 points returned +3.5% ROI over 180 picks. It's a small sample, and the site shows it next to the full record (−4.1%).
>
> Python, Dash, pandas and Plotly, with tests, CI and Docker, on Render.
>
> What would you dig into next? 👇
> https://betting-dashboard.onrender.com
>
> #DataScience #MachineLearning #Python #SportsAnalytics

**Shorter variant (about 500 characters):**

> I rebuilt an old basketball prediction project into a dashboard that grades every pick the model ever published, including the losing ones.
>
> The headline: betting totals only when the model disagreed with the bookmaker by more than 2.5 points returned +3.5% ROI over 180 picks, against −4.1% for every pick. It's small-sample, so it's labelled that way.
>
> Python · Dash · pandas · Plotly · Docker
> https://betting-dashboard.onrender.com

---

## LinkedIn "Featured" item

- **Link:** https://betting-dashboard.onrender.com
- **Title:** Courtside Analytics: a basketball prediction model, graded honestly
- **Description:** A dashboard that grades 1,292 published predictions against final scores and explores 35k games across 11 leagues. The recommended strategy (edge > 2.5) returned +3.5% ROI; the full record is shown alongside. Python, Dash, pandas, Plotly, Docker.

---

## Portfolio site project card

**Card text**

- **Title:** Courtside Analytics
- **Blurb:** A basketball score-prediction model with an honest track record: 1,292 published picks graded against final scores, plus 35k historical games to explore. I recovered the project from a broken state, fixed the data and grading bugs I found, and rebuilt it as a tested, containerised Dash app.
- **Tags:** Python · pandas · Dash · Plotly · Machine learning · Docker · CI
- **Links:** Live demo · Code

**Markdown** (for a Jekyll or Markdown-based page):

```markdown
### [Courtside Analytics](https://betting-dashboard.onrender.com)

![Courtside Analytics](https://raw.githubusercontent.com/Konstantinos-Sakellariou/betting-dashboard/main/src/betting_dashboard/assets/og-image.png)

A basketball score-prediction model with an honest track record: 1,292 published picks graded against final scores, plus 35k historical games to explore. Recovered from a broken state, with its data and grading bugs fixed, and rebuilt as a tested, containerised Dash app.

`Python` `pandas` `Dash` `Plotly` `Machine learning` `Docker` `CI`

[Live demo](https://betting-dashboard.onrender.com) · [Code](https://github.com/Konstantinos-Sakellariou/betting-dashboard)
```

**HTML** (adapt the class names to the site's existing cards):

```html
<article class="project-card">
  <a href="https://betting-dashboard.onrender.com">
    <img src="https://raw.githubusercontent.com/Konstantinos-Sakellariou/betting-dashboard/main/src/betting_dashboard/assets/og-image.png"
         alt="Courtside Analytics dashboard preview" loading="lazy" width="1200" height="630">
  </a>
  <h3>Courtside Analytics</h3>
  <p>A basketball score-prediction model with an honest track record: 1,292 published picks graded
     against final scores, plus 35k historical games to explore. Recovered from a broken state and
     rebuilt as a tested, containerised Dash app.</p>
  <ul class="tags">
    <li>Python</li><li>pandas</li><li>Dash</li><li>Plotly</li><li>Machine learning</li><li>Docker</li>
  </ul>
  <p>
    <a href="https://betting-dashboard.onrender.com">Live demo</a> ·
    <a href="https://github.com/Konstantinos-Sakellariou/betting-dashboard">Code</a>
  </p>
</article>
```

To add this to https://konstantinos-sakellariou.github.io/ for you, a Claude session needs that repository (`Konstantinos-Sakellariou/konstantinos-sakellariou.github.io`) added. It would then follow the site's existing structure and open a PR for you to review.
