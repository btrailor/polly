"""
GitHub Integration
Fetches and indexes repositories, issues, and pull requests
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
import logging

from .base import Integration, IntegrationStatus, IntegrationError

logger = logging.getLogger(__name__)


class GitHubIntegration(Integration):
    """
    GitHub integration for Polly.
    
    Fetches and indexes:
    - User's repositories
    - Repository READMEs
    - Issues and PRs
    - Code search results
    """
    
    GITHUB_API_BASE = "https://api.github.com"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("github", config)
        self.token: Optional[str] = None
        self.username: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def connect(self, credentials: Dict[str, str]) -> bool:
        """
        Connect to GitHub using OAuth token.
        
        Args:
            credentials: {"token": "gho_..."}
        """
        self.token = credentials.get("token")
        if not self.token:
            raise IntegrationError("No token provided")
        
        # Create HTTP session
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Polly-AI"
            }
        )
        
        # Verify token and get username
        try:
            success = await self.test_connection()
            if success:
                self._set_status(IntegrationStatus.CONNECTED)
                logger.info(f"GitHub connected as {self.username}")
            return success
        except Exception as e:
            await self.disconnect()
            raise IntegrationError(f"Connection failed: {e}")
    
    async def disconnect(self) -> bool:
        """Disconnect from GitHub."""
        if self.session:
            await self.session.close()
            self.session = None
        
        self.token = None
        self.username = None
        self._set_status(IntegrationStatus.DISCONNECTED)
        return True
    
    async def test_connection(self) -> bool:
        """Test GitHub connection and get user info."""
        if not self.session:
            return False
        
        try:
            async with self.session.get(f"{self.GITHUB_API_BASE}/user") as resp:
                if resp.status == 200:
                    user_data = await resp.json()
                    self.username = user_data.get("login")
                    return True
                else:
                    error_text = await resp.text()
                    logger.error(f"GitHub auth failed: {resp.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"GitHub connection test failed: {e}")
            return False
    
    async def fetch_data(
        self,
        include_repos: bool = True,
        include_issues: bool = False,
        include_prs: bool = False,
        repo_limit: int = 30,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch data from GitHub.
        
        Args:
            include_repos: Fetch user's repositories
            include_issues: Fetch issues (across all repos)
            include_prs: Fetch pull requests
            repo_limit: Max number of repos to fetch
        
        Returns:
            Dict with fetched data
        """
        if not self.session:
            raise IntegrationError("Not connected")
        
        data = {
            "repositories": [],
            "issues": [],
            "pull_requests": [],
            "metadata": {
                "fetched_at": datetime.now().isoformat(),
                "username": self.username
            }
        }
        
        try:
            if include_repos:
                repos = await self._fetch_repositories(repo_limit)
                data["repositories"] = repos
                logger.info(f"Fetched {len(repos)} repositories")
            
            if include_issues:
                issues = await self._fetch_issues()
                data["issues"] = issues
                logger.info(f"Fetched {len(issues)} issues")
            
            if include_prs:
                prs = await self._fetch_pull_requests()
                data["pull_requests"] = prs
                logger.info(f"Fetched {len(prs)} pull requests")
            
            return data
            
        except Exception as e:
            logger.error(f"GitHub fetch failed: {e}")
            raise IntegrationError(f"Fetch failed: {e}")
    
    async def _fetch_repositories(self, limit: int = 30) -> List[Dict]:
        """Fetch user's repositories."""
        repos = []
        
        try:
            # Fetch user's repos (sorted by update time)
            url = f"{self.GITHUB_API_BASE}/user/repos"
            params = {
                "sort": "updated",
                "per_page": limit,
                "affiliation": "owner,collaborator"
            }
            
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    repo_data = await resp.json()
                    
                    for repo in repo_data:
                        # Fetch README if available
                        readme_content = await self._fetch_readme(
                            repo["owner"]["login"],
                            repo["name"]
                        )
                        
                        repos.append({
                            "id": repo["id"],
                            "name": repo["name"],
                            "full_name": repo["full_name"],
                            "description": repo.get("description", ""),
                            "url": repo["html_url"],
                            "language": repo.get("language"),
                            "stars": repo["stargazers_count"],
                            "forks": repo["forks_count"],
                            "updated_at": repo["updated_at"],
                            "readme": readme_content,
                            "topics": repo.get("topics", []),
                            "private": repo["private"]
                        })
                else:
                    logger.error(f"Failed to fetch repos: {resp.status}")
        
        except Exception as e:
            logger.error(f"Error fetching repositories: {e}")
        
        return repos
    
    async def _fetch_readme(self, owner: str, repo: str) -> Optional[str]:
        """Fetch repository README."""
        try:
            url = f"{self.GITHUB_API_BASE}/repos/{owner}/{repo}/readme"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    readme_data = await resp.json()
                    # README content is base64 encoded
                    import base64
                    content = base64.b64decode(readme_data["content"]).decode("utf-8")
                    return content
                return None
        except Exception as e:
            logger.debug(f"No README for {owner}/{repo}: {e}")
            return None
    
    async def _fetch_issues(self, state: str = "open") -> List[Dict]:
        """Fetch issues across all repos."""
        issues = []
        
        try:
            url = f"{self.GITHUB_API_BASE}/issues"
            params = {
                "filter": "assigned",
                "state": state,
                "per_page": 50
            }
            
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    issue_data = await resp.json()
                    
                    for issue in issue_data:
                        # Skip PRs (they show up in issues endpoint too)
                        if "pull_request" in issue:
                            continue
                        
                        issues.append({
                            "id": issue["id"],
                            "number": issue["number"],
                            "title": issue["title"],
                            "body": issue.get("body", ""),
                            "state": issue["state"],
                            "url": issue["html_url"],
                            "repo": issue["repository_url"].split("/")[-1],
                            "created_at": issue["created_at"],
                            "updated_at": issue["updated_at"],
                            "labels": [label["name"] for label in issue.get("labels", [])]
                        })
        
        except Exception as e:
            logger.error(f"Error fetching issues: {e}")
        
        return issues
    
    async def _fetch_pull_requests(self) -> List[Dict]:
        """Fetch user's pull requests."""
        prs = []
        
        try:
            url = f"{self.GITHUB_API_BASE}/search/issues"
            params = {
                "q": f"is:pr author:{self.username}",
                "sort": "updated",
                "per_page": 50
            }
            
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    search_data = await resp.json()
                    
                    for pr in search_data.get("items", []):
                        prs.append({
                            "id": pr["id"],
                            "number": pr["number"],
                            "title": pr["title"],
                            "body": pr.get("body", ""),
                            "state": pr["state"],
                            "url": pr["html_url"],
                            "created_at": pr["created_at"],
                            "updated_at": pr["updated_at"]
                        })
        
        except Exception as e:
            logger.error(f"Error fetching PRs: {e}")
        
        return prs
    
    def format_for_rag(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format GitHub data for RAG indexing.
        
        Creates documents for:
        - Repository info + README
        - Issues
        - Pull requests
        """
        documents = []
        
        # Format repositories
        for repo in data.get("repositories", []):
            # Create document for each repo
            content_parts = [
                f"Repository: {repo['full_name']}",
                f"Description: {repo['description']}" if repo['description'] else "",
                f"Language: {repo['language']}" if repo['language'] else "",
                f"Stars: {repo['stars']}, Forks: {repo['forks']}",
                f"Topics: {', '.join(repo['topics'])}" if repo['topics'] else "",
            ]
            
            # Add README if available
            if repo.get('readme'):
                content_parts.append("\n--- README ---\n")
                # Truncate very long READMEs
                readme = repo['readme'][:5000]
                content_parts.append(readme)
            
            content = "\n".join(filter(None, content_parts))
            
            documents.append({
                "content": content,
                "metadata": {
                    "source": "github",
                    "type": "repository",
                    "id": str(repo['id']),
                    "name": repo['full_name'],
                    "url": repo['url'],
                    "language": repo.get('language'),
                    "updated_at": repo['updated_at'],
                    "private": repo['private']
                }
            })
        
        # Format issues
        for issue in data.get("issues", []):
            content = f"""Issue: {issue['title']}
Repository: {issue['repo']}
Status: {issue['state']}
Labels: {', '.join(issue['labels'])}

{issue['body']}"""
            
            documents.append({
                "content": content,
                "metadata": {
                    "source": "github",
                    "type": "issue",
                    "id": str(issue['id']),
                    "number": issue['number'],
                    "url": issue['url'],
                    "state": issue['state'],
                    "created_at": issue['created_at']
                }
            })
        
        # Format pull requests
        for pr in data.get("pull_requests", []):
            content = f"""Pull Request: {pr['title']}
Status: {pr['state']}

{pr['body']}"""
            
            documents.append({
                "content": content,
                "metadata": {
                    "source": "github",
                    "type": "pull_request",
                    "id": str(pr['id']),
                    "number": pr['number'],
                    "url": pr['url'],
                    "state": pr['state'],
                    "created_at": pr['created_at']
                }
            })
        
        return documents
