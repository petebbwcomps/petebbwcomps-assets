# deploy_videos

This directory contains `videos.json` and `thumbnails/` intended to be published as a static site (GitHub Pages or Netlify).

To publish on GitHub Pages (recommended):

1. Create a new GitHub repository (public) named `my-videos-json` (or any name).
2. On your machine, run the following PowerShell commands from this `deploy_videos` folder:

```powershell
# initialize a new repo and push
git init
git add .
git commit -m "Add videos.json and thumbnails"
# replace <GIT-URL> with the HTTPS repo URL from GitHub (e.g., https://github.com/you/my-videos-json.git)
git remote add origin <GIT-URL>
git branch -M main
git push -u origin main
```

3. Enable GitHub Pages in the repository settings: Settings → Pages → Build and deployment → Branch: `main` / Folder: `/ (root)` → Save. Your files will be available at `https://<user>.github.io/<repo>/videos.json` and `https://<user>.github.io/<repo>/thumbnails/placeholder.svg`.

4. In your Vite app `.env`, set:

```
VITE_VIDEOS_URL=https://<user>.github.io/<repo>/videos.json
```

5. Restart your dev server: `npm run dev`.

Notes:
- Netlify or Vercel work equally well; just deploy this folder as a static site and use the generated URL for `VITE_VIDEOS_URL`.
- If you prefer, I can create the minimal git commands as a PowerShell script that prompts for the repo URL.
