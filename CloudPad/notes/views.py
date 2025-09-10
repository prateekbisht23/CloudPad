from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Note
import requests
import json
from datetime import datetime, timedelta

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def repo_finder(request):
    """Find trending repositories for contribution"""
    return render(request, 'repo_finder.html')

def find_repositories(request):
    """API endpoint to search for contribution-friendly repositories"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Get search parameters
    language = request.GET.get('language', '')
    topic = request.GET.get('topic', '')
    min_stars = request.GET.get('min_stars', '10')
    
    try:
        # Search for repositories using GitHub API
        repositories = search_github_repositories(language, topic, min_stars)
        return JsonResponse({'repositories': repositories})
    except Exception as e:
        # If GitHub API fails, try fallback
        try:
            repositories = get_fallback_repositories(language, topic, min_stars)
            return JsonResponse({'repositories': repositories})
        except Exception:
            return JsonResponse({'error': 'Unable to fetch repositories at this time'}, status=500)

def search_github_repositories(language='', topic='', min_stars='10'):
    """Search GitHub for contribution-friendly repositories"""
    
    # Build search query
    query_parts = []
    
    # Add language filter
    if language:
        query_parts.append(f'language:{language}')
    
    # Add topic filter
    if topic:
        query_parts.append(f'topic:{topic}')
    
    # Add stars filter
    try:
        stars = int(min_stars)
        query_parts.append(f'stars:>={stars}')
    except ValueError:
        query_parts.append('stars:>=10')
    
    # Add filters for contribution-friendly repositories
    query_parts.extend([
        'is:public',  # Public repositories only
        'archived:false',  # Not archived
    ])
    
    # Recent activity (updated in last 6 months)
    six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    query_parts.append(f'pushed:>={six_months_ago}')
    
    query = ' '.join(query_parts)
    
    # GitHub API endpoint
    url = 'https://api.github.com/search/repositories'
    
    params = {
        'q': query,
        'sort': 'updated',  # Sort by recently updated
        'order': 'desc',
        'per_page': 15
    }
    
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'CloudPad-RepoFinder'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 403:
            # Rate limited, return some popular repositories as fallback
            return get_fallback_repositories(language, topic, min_stars)
        
        if response.status_code != 200:
            raise Exception(f'GitHub API error: {response.status_code}')
        
        data = response.json()
        repositories = []
        
        for repo in data.get('items', []):
            # Get additional repository info
            repo_data = {
                'name': repo['name'],
                'full_name': repo['full_name'],
                'description': repo['description'] or 'No description available',
                'html_url': repo['html_url'],
                'stargazers_count': repo['stargazers_count'],
                'forks_count': repo['forks_count'],
                'language': repo['language'],
                'updated_at': repo['updated_at'],
                'topics': repo.get('topics', []),
                'open_issues_count': repo['open_issues_count'],
                'owner': {
                    'login': repo['owner']['login'],
                    'avatar_url': repo['owner']['avatar_url'],
                    'html_url': repo['owner']['html_url']
                },
                'good_first_issues': 1,  # Assume at least 1 for search results
                'help_wanted_issues': 1,  # Assume at least 1 for search results
                'has_contributing_guide': True,  # Assume good repos have this
                'has_code_of_conduct': True  # Assume good repos have this
            }
            
            repositories.append(repo_data)
        
        return repositories
        
    except requests.RequestException:
        # Network error, return fallback
        return get_fallback_repositories(language, topic, min_stars)

def get_fallback_repositories(language='', topic='', min_stars='10'):
    """Return a curated list of contribution-friendly repositories as fallback"""
    
    # Curated list of great repositories for contribution
    fallback_repos = [
        {
            'name': 'first-contributions',
            'full_name': 'firstcontributions/first-contributions',
            'description': 'Help beginners to contribute to open source projects',
            'html_url': 'https://github.com/firstcontributions/first-contributions',
            'stargazers_count': 44000,
            'forks_count': 78000,
            'language': 'None',
            'updated_at': '2024-09-10T12:00:00Z',
            'topics': ['good-first-issue', 'hacktoberfest', 'beginner-friendly'],
            'open_issues_count': 50,
            'owner': {
                'login': 'firstcontributions',
                'avatar_url': 'https://avatars.githubusercontent.com/u/35373879?v=4',
                'html_url': 'https://github.com/firstcontributions'
            },
            'good_first_issues': 10,
            'help_wanted_issues': 5,
            'has_contributing_guide': True,
            'has_code_of_conduct': True
        },
        {
            'name': 'awesome-for-beginners',
            'full_name': 'MunGell/awesome-for-beginners',
            'description': 'A list of awesome beginners-friendly projects',
            'html_url': 'https://github.com/MunGell/awesome-for-beginners',
            'stargazers_count': 68000,
            'forks_count': 8500,
            'language': 'None',
            'updated_at': '2024-09-08T10:30:00Z',
            'topics': ['awesome', 'beginners', 'good-first-issue'],
            'open_issues_count': 20,
            'owner': {
                'login': 'MunGell',
                'avatar_url': 'https://avatars.githubusercontent.com/u/830478?v=4',
                'html_url': 'https://github.com/MunGell'
            },
            'good_first_issues': 8,
            'help_wanted_issues': 12,
            'has_contributing_guide': True,
            'has_code_of_conduct': True
        },
        {
            'name': 'django',
            'full_name': 'django/django',
            'description': 'The Django web framework for perfectionists with deadlines',
            'html_url': 'https://github.com/django/django',
            'stargazers_count': 79000,
            'forks_count': 31000,
            'language': 'Python',
            'updated_at': '2024-09-10T08:15:00Z',
            'topics': ['python', 'web-framework', 'django'],
            'open_issues_count': 180,
            'owner': {
                'login': 'django',
                'avatar_url': 'https://avatars.githubusercontent.com/u/27804?v=4',
                'html_url': 'https://github.com/django'
            },
            'good_first_issues': 25,
            'help_wanted_issues': 40,
            'has_contributing_guide': True,
            'has_code_of_conduct': True
        },
        {
            'name': 'react',
            'full_name': 'facebook/react',
            'description': 'The React library for building user interfaces',
            'html_url': 'https://github.com/facebook/react',
            'stargazers_count': 228000,
            'forks_count': 46000,
            'language': 'JavaScript',
            'updated_at': '2024-09-10T14:20:00Z',
            'topics': ['javascript', 'react', 'frontend'],
            'open_issues_count': 600,
            'owner': {
                'login': 'facebook',
                'avatar_url': 'https://avatars.githubusercontent.com/u/69631?v=4',
                'html_url': 'https://github.com/facebook'
            },
            'good_first_issues': 15,
            'help_wanted_issues': 30,
            'has_contributing_guide': True,
            'has_code_of_conduct': True
        },
        {
            'name': 'tensorflow',
            'full_name': 'tensorflow/tensorflow',
            'description': 'An Open Source Machine Learning Framework for Everyone',
            'html_url': 'https://github.com/tensorflow/tensorflow',
            'stargazers_count': 185000,
            'forks_count': 74000,
            'language': 'C++',
            'updated_at': '2024-09-10T16:45:00Z',
            'topics': ['machine-learning', 'tensorflow', 'deep-learning'],
            'open_issues_count': 2100,
            'owner': {
                'login': 'tensorflow',
                'avatar_url': 'https://avatars.githubusercontent.com/u/15658638?v=4',
                'html_url': 'https://github.com/tensorflow'
            },
            'good_first_issues': 35,
            'help_wanted_issues': 85,
            'has_contributing_guide': True,
            'has_code_of_conduct': True
        },
        {
            'name': 'freeCodeCamp',
            'full_name': 'freeCodeCamp/freeCodeCamp',
            'description': 'freeCodeCamp.org\'s open-source codebase and curriculum',
            'html_url': 'https://github.com/freeCodeCamp/freeCodeCamp',
            'stargazers_count': 401000,
            'forks_count': 37000,
            'language': 'TypeScript',
            'updated_at': '2024-09-10T11:30:00Z',
            'topics': ['education', 'freecodecamp', 'learn-to-code'],
            'open_issues_count': 300,
            'owner': {
                'login': 'freeCodeCamp',
                'avatar_url': 'https://avatars.githubusercontent.com/u/9892522?v=4',
                'html_url': 'https://github.com/freeCodeCamp'
            },
            'good_first_issues': 50,
            'help_wanted_issues': 100,
            'has_contributing_guide': True,
            'has_code_of_conduct': True
        },
        {
            'name': 'scikit-learn',
            'full_name': 'scikit-learn/scikit-learn',
            'description': 'scikit-learn: machine learning in Python',
            'html_url': 'https://github.com/scikit-learn/scikit-learn',
            'stargazers_count': 59000,
            'forks_count': 25000,
            'language': 'Python',
            'updated_at': '2024-09-10T09:45:00Z',
            'topics': ['machine-learning', 'python', 'scikit-learn'],
            'open_issues_count': 2200,
            'owner': {
                'login': 'scikit-learn',
                'avatar_url': 'https://avatars.githubusercontent.com/u/365630?v=4',
                'html_url': 'https://github.com/scikit-learn'
            },
            'good_first_issues': 45,
            'help_wanted_issues': 120,
            'has_contributing_guide': True,
            'has_code_of_conduct': True
        },
        {
            'name': 'nodejs',
            'full_name': 'nodejs/node',
            'description': 'Node.js JavaScript runtime',
            'html_url': 'https://github.com/nodejs/node',
            'stargazers_count': 107000,
            'forks_count': 29000,
            'language': 'JavaScript',
            'updated_at': '2024-09-10T15:20:00Z',
            'topics': ['javascript', 'nodejs', 'runtime'],
            'open_issues_count': 1800,
            'owner': {
                'login': 'nodejs',
                'avatar_url': 'https://avatars.githubusercontent.com/u/9950313?v=4',
                'html_url': 'https://github.com/nodejs'
            },
            'good_first_issues': 20,
            'help_wanted_issues': 60,
            'has_contributing_guide': True,
            'has_code_of_conduct': True
        }
    ]
    
    # Filter based on criteria
    filtered_repos = []
    min_stars_int = int(min_stars) if min_stars.isdigit() else 10
    
    for repo in fallback_repos:
        # Filter by language
        if language and repo['language'] and repo['language'] != 'None' and language.lower() != repo['language'].lower():
            continue
            
        # Filter by minimum stars
        if repo['stargazers_count'] < min_stars_int:
            continue
            
        # Filter by topic (simple matching)
        if topic:
            repo_topics_str = ' '.join(repo['topics']).lower()
            repo_desc = repo['description'].lower()
            topic_lower = topic.lower().replace('-', ' ')
            if topic_lower not in repo_topics_str and topic_lower not in repo_desc:
                continue
        
        filtered_repos.append(repo)
    
    return filtered_repos[:10]  # Return max 10 results

def get_contribution_info(repo_full_name):
    """Get contribution-specific information for a repository"""
    base_url = f'https://api.github.com/repos/{repo_full_name}'
    
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'CloudPad-RepoFinder'
    }
    
    contrib_info = {
        'good_first_issues': 0,
        'help_wanted_issues': 0,
        'has_contributing_guide': False,
        'has_code_of_conduct': False
    }
    
    # Check for good first issues
    try:
        issues_url = f'{base_url}/issues'
        params = {'labels': 'good first issue', 'state': 'open', 'per_page': 1}
        response = requests.get(issues_url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            # GitHub returns total count in Link header or we can check if any issues exist
            contrib_info['good_first_issues'] = len(response.json())
    except Exception:
        pass
    
    # Check for help wanted issues
    try:
        params = {'labels': 'help wanted', 'state': 'open', 'per_page': 1}
        response = requests.get(issues_url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            contrib_info['help_wanted_issues'] = len(response.json())
    except Exception:
        pass
    
    # Check for contributing guide and code of conduct
    try:
        contents_url = f'{base_url}/contents'
        response = requests.get(contents_url, headers=headers, timeout=5)
        if response.status_code == 200:
            files = response.json()
            file_names = [f['name'].lower() for f in files if isinstance(f, dict)]
            
            contrib_info['has_contributing_guide'] = any(
                'contributing' in name for name in file_names
            )
            contrib_info['has_code_of_conduct'] = any(
                'code_of_conduct' in name or 'code-of-conduct' in name 
                for name in file_names
            )
    except Exception:
        pass
    
    return contrib_info

def note_view(request, url_id):
    note, created = Note.objects.get_or_create(url_id = url_id)
    return render(request, 'note.html', {'note':note})

def save_note(request, url_id):
    if request.method == "POST":
        content = request.POST.get("content", "")
        note, created = Note.objects.get_or_create(url_id=url_id)
        
        note.content = content
        note.save()
        return JsonResponse({"status": "success", "content": note.content})
    
    return JsonResponse({"status": "failed"}, status=400)


def load_note(request, url_id):
    note, created = Note.objects.get_or_create(url_id=url_id)
    return JsonResponse({"content": note.content})



# def upload_file(file_path, file):
#     bucket_name = "cloudpad-files"
#     note_id = "test"  # This should be dynamic based on your app

#     try:
#         # Ensure the file is stored inside a folder (like note_id/)
#         full_path = f"{note_id}/{os.path.basename(file_path)}"

#         res = supabase.storage.from_(bucket_name).upload(
#             full_path, file, file_options={"content-type": "application/octet-stream"}
#         )

#         return {"success": True, "message": "File uploaded successfully", "data": res}
#     except Exception as e:
#         return {"success": False, "error": str(e)}


# def list_files(request, note_id):
#     bucket_name = "cloudpad-files"
    
#     response = supabase.storage.from_(bucket_name).list(path=note_id)

#     if response:
#         files = [
#             {
#                 "file_name": file["name"],
#                 "file_url": f"{supabase_url}/storage/v1/object/public/{bucket_name}/{note_id}/{file['name']}",
#             }
#             for file in response
#         ]
#         return JsonResponse({"files": files})

#     return JsonResponse({"files": []})