export const validateGitHubUrl = (url: string): { valid: boolean; error?: string; owner?: string; repo?: string } => {
  const trimmed = url.trim();

  if (!trimmed) {
    return { valid: false, error: 'Repository URL is required' };
  }

  const githubUrlPattern = /^https?:\/\/github\.com\/([a-zA-Z0-9_-]+)\/([a-zA-Z0-9._-]+)/;
  const match = trimmed.match(githubUrlPattern);

  if (!match) {
    return { valid: false, error: 'Invalid GitHub URL format. Expected: https://github.com/owner/repo' };
  }

  const owner = match[1];
  const repo = match[2].replace(/\.git$/, '');

  if (owner.length > 255) {
    return { valid: false, error: 'Owner name is too long' };
  }

  if (repo.length > 100) {
    return { valid: false, error: 'Repository name is too long' };
  }

  if (owner === '' || repo === '') {
    return { valid: false, error: 'Owner and repository name are required' };
  }

  return { valid: true, owner, repo };
};

export const isPublicRepo = async (owner: string, repo: string): Promise<boolean> => {
  try {
    const response = await fetch(`https://api.github.com/repos/${owner}/${repo}`, {
      method: 'HEAD',
      headers: {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
      },
    });
    return response.ok;
  } catch {
    return false;
  }
};