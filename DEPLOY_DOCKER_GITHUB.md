# Deploy with Docker and GitHub

## Section 1: Build and Run with Docker Locally

- `docker build -t roi-backend:latest .`
  - Builds a Docker image named `roi-backend` using the Dockerfile in the project root.
- `docker run -p 8000:8000 roi-backend:latest`
  - Starts a container from the image and maps container port `8000` to your local `8000`.
- Test at: `http://localhost:8000/docs`
  - Opens FastAPI’s interactive Swagger UI to verify endpoints.

## Section 2: Step-by-step Git + GitHub Commands

- `git init`
  - Initializes a new Git repository in the current folder.
- `git add .`
  - Stages all files for commit.
- `git commit -m "Initial ROI backend with Docker"`
  - Creates a commit with a descriptive message.
- `git branch -M main`
  - Renames the current branch to `main` and sets it as the primary branch.
- `git remote add origin <YOUR_GITHUB_REPO_URL>`
  - Adds your GitHub repository as the remote named `origin`.
- `git push -u origin main`
  - Pushes the `main` branch to GitHub and sets upstream tracking for future pushes.