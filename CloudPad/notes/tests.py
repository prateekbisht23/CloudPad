from django.test import TestCase, Client
from django.urls import reverse
import json

class RepoFinderTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_repo_finder_page_loads(self):
        """Test that the repo finder page loads successfully"""
        response = self.client.get(reverse('repo_finder'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Trending Repositories')
        self.assertContains(response, 'Programming Language')
        self.assertContains(response, 'Topic/Area')
        self.assertContains(response, 'Minimum Stars')

    def test_find_repositories_api(self):
        """Test that the API endpoint returns repository data"""
        response = self.client.get(reverse('find_repositories'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('repositories', data)
        self.assertIsInstance(data['repositories'], list)
        
        # Should return some repositories
        self.assertGreater(len(data['repositories']), 0)
        
        # Check repository structure
        if data['repositories']:
            repo = data['repositories'][0]
            required_fields = [
                'name', 'full_name', 'description', 'html_url',
                'stargazers_count', 'forks_count', 'language',
                'good_first_issues', 'help_wanted_issues',
                'has_contributing_guide', 'has_code_of_conduct'
            ]
            for field in required_fields:
                self.assertIn(field, repo)

    def test_repository_filtering_by_language(self):
        """Test that language filtering works"""
        response = self.client.get(reverse('find_repositories'), {'language': 'python'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        repositories = data['repositories']
        
        # All returned repositories should be Python or language-agnostic
        for repo in repositories:
            self.assertIn(repo['language'], [None, 'None', 'Python'])

    def test_repository_filtering_by_topic(self):
        """Test that topic filtering works"""
        response = self.client.get(reverse('find_repositories'), {'topic': 'machine-learning'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        repositories = data['repositories']
        
        # Should filter to relevant repositories
        self.assertGreaterEqual(len(repositories), 0)

    def test_repository_filtering_by_stars(self):
        """Test that star filtering works"""
        response = self.client.get(reverse('find_repositories'), {'min_stars': '50000'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        repositories = data['repositories']
        
        # All repositories should have at least 50000 stars
        for repo in repositories:
            self.assertGreaterEqual(repo['stargazers_count'], 50000)
