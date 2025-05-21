# Assignment

This project consists of a **backend**, **frontend**, and **Redis** integration for managing various third-party OAuth integrations (e.g., HubSpot, Airtable, and Notion).

## Prerequisites

Make sure you have the following tools installed:

- **Docker**: for containerization
- **Docker Compose**: to orchestrate the services (frontend, backend, and Redis)
- **git**: to clone the repository

## Quick Start

Follow these steps to get the project up and running with a single command:

### 1. Clone the repository

First, clone the repository to your local machine.

```bash
git clone https://your-repo-url.git
cd your-repo-directory
```
### Build and start the services using Docker Compose
You can now start the project with a single command. This will build and run the backend, frontend, and Redis services in containers.

```bash
docker-compose up --build
```
This command will:

Build the Docker images for frontend and backend (if not already built).

Pull the Redis image from Docker Hub and start it.

Start the backend on port 8000 and the frontend on port 3000.

All configurations will be loaded automatically from the .env file.

4. Access the application
Frontend: Open http://localhost:3000 in your browser to access the React frontend.

Backend: The FastAPI backend will be available at http://localhost:8000.

5. Stopping the services
To stop all running services, simply run:

```bash
docker-compose down
```

# Folder Structure 
```base
project-root/
│
├── backend/                   # Backend code (FastAPI)
│   ├── Dockerfile.backend      # Dockerfile for backend
│   ├── .dockerignore           # Backend Docker ignore file
│   ├── main.py                 # Main backend FastAPI file
│   ├── requirements.txt        # Python dependencies
│   └── ...other backend files...
│
├── frontend/                  # Frontend code (React)
│   ├── Dockerfile.frontend     # Dockerfile for frontend
│   ├── .dockerignore           # Frontend Docker ignore file
│   ├── package.json            # Frontend dependencies
│   ├── package-lock.json       # Frontend lock file
│   └── ...other frontend files...
│
├── docker-compose.yml          # Docker Compose file
├── .env.example                # Example environment file (template)
└── README.md                   # Project README (this file)

``` 

## Configuration

### Environment Variables

The following environment variables are required for the project to work:

#### Redis Configuration
- `REDIS_HOST`: The host where Redis is running (default: `redis` for Docker container).
- `REDIS_PORT`: The Redis port (default: `6379`).

#### HubSpot Configuration
- `HUBSPOT_CLIENT_ID`: Your HubSpot client ID.
- `HUBSPOT_CLIENT_SECRET`: Your HubSpot client secret.
- `HUBSPOT_REDIRECT_URI`: The HubSpot OAuth redirect URL (default: `http://localhost:8000/integrations/hubspot/oauth2callback`).
- `HUBSPOT_AUTHORIZATION_URL`: The HubSpot OAuth authorization URL.
- `HUBSPOT_TOKEN_URL`: The HubSpot OAuth token URL.

#### Airtable Configuration
- `AIRTABLE_CLIENT_ID`: Your Airtable client ID.
- `AIRTABLE_CLIENT_SECRET`: Your Airtable client secret.
- `AIRTABLE_REDIRECT_URI`: The Airtable OAuth redirect URL (default: `http://localhost:8000/integrations/airtable/oauth2callback`).
- `AIRTABLE_TOKEN_URL`: The Airtable OAuth token URL.

#### Notion Configuration
- `NOTION_CLIENT_ID`: Your Notion client ID.
- `NOTION_CLIENT_SECRET`: Your Notion client secret.
- `NOTION_REDIRECT_URI`: The Notion OAuth redirect URL (default: `http://localhost:8000/integrations/notion/oauth2callback`).
- `NOTION_TOKEN_URL`: The Notion OAuth token URL.

---

These values should be set in your `.env` file.

Example `.env`:

```env
# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# HubSpot Configuration
HUBSPOT_CLIENT_ID=your_hubspot_client_id_here
HUBSPOT_CLIENT_SECRET=your_hubspot_client_secret_here
HUBSPOT_REDIRECT_URI=http://localhost:8000/integrations/hubspot/oauth2callback
HUBSPOT_AUTHORIZATION_URL=https://app-na2.hubspot.com/oauth/authorize
HUBSPOT_TOKEN_URL=https://api.hubapi.com/oauth/v1/token

# Airtable Configuration
AIRTABLE_CLIENT_ID=your_airtable_client_id_here
AIRTABLE_CLIENT_SECRET=your_airtable_client_secret_here
AIRTABLE_REDIRECT_URI=http://localhost:8000/integrations/airtable/oauth2callback
AIRTABLE_TOKEN_URL=https://airtable.com/oauth2/v1/token

# Notion Configuration
NOTION_CLIENT_ID=your_notion_client_id_here
NOTION_CLIENT_SECRET=your_notion_client_secret_here
NOTION_REDIRECT_URI=http://localhost:8000/integrations/notion/oauth2callback
NOTION_TOKEN_URL=https://api.notion.com/v1/oauth/token
