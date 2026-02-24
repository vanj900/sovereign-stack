# GitHub Pages Deployment Setup

This document explains how to enable GitHub Pages for the Red Flag Auditor repository.

## Prerequisites

- Repository must be public (or have GitHub Pro/Team for private repo pages)
- GitHub Actions must be enabled for the repository

## Enable GitHub Pages

Follow these steps to enable GitHub Pages deployment:

1. **Go to Repository Settings**
   - Navigate to your repository on GitHub
   - Click on "Settings" tab

2. **Navigate to Pages Settings**
   - In the left sidebar, click on "Pages" under "Code and automation"

3. **Configure Source**
   - Under "Build and deployment"
   - Set **Source** to: `GitHub Actions`
   - This will use the workflow defined in `.github/workflows/pages.yml`

4. **Save and Deploy**
   - The configuration will save automatically
   - Push to the `main` branch to trigger the first deployment
   - Or use the "Actions" tab to manually trigger a workflow run

## Accessing Your Site

Once deployed, your site will be available at:
```
https://vanj900.github.io/vanj900-Red-Flag-Auditor/
```

## Workflow Details

The GitHub Actions workflow (`.github/workflows/pages.yml`) will:
- Trigger on every push to the `main` branch
- Can also be triggered manually from the Actions tab
- Build and deploy all files from the repository root
- Use GitHub's native Pages deployment actions

## Manual Deployment

To trigger a manual deployment:
1. Go to the "Actions" tab in your repository
2. Click on "Deploy to GitHub Pages" workflow
3. Click "Run workflow" button
4. Select the branch (usually `main`)
5. Click "Run workflow"

## Troubleshooting

### Deployment Fails
- Check that GitHub Pages is enabled in repository settings
- Ensure the repository is public or you have the right plan
- Review the Actions logs for specific errors

### 404 Error
- Wait a few minutes after first deployment
- Clear your browser cache
- Verify the index.html file exists in the repository root

### Changes Not Appearing
- Ensure changes are pushed to the `main` branch
- Check the Actions tab to verify the workflow ran successfully
- Clear browser cache or use incognito mode

## Local Testing

To test the site locally before deploying:

```bash
# Using Python
python3 -m http.server 8080

# Using Node.js (if installed)
npx serve

# Using PHP (if installed)
php -S localhost:8080
```

Then open `http://localhost:8080` in your browser.

## Security

- All HTML/CSS/JavaScript runs in the user's browser
- No server-side processing
- No data collection or transmission
- Perfect for privacy-focused tools

## Additional Configuration

### Custom Domain (Optional)
If you want to use a custom domain:
1. Add a `CNAME` file with your domain name
2. Configure DNS settings with your domain provider
3. Update GitHub Pages settings to use your custom domain

### Custom 404 Page (Optional)
Create a `404.html` file in the repository root for custom error pages.
