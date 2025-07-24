from flask import Blueprint, request, jsonify, send_file
from flask_cors import cross_origin
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import io
import tempfile
import os

llms_bp = Blueprint('llms', __name__)

class LLMSGenerator:
    def __init__(self, url):
        self.url = url
        self.domain = urlparse(url).netloc
        self.site_data = {}
        
    def analyze_website(self):
        """Analyze the website and extract relevant information"""
        try:
            # Fetch the main page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic information
            self.site_data['title'] = self._extract_title(soup)
            self.site_data['description'] = self._extract_description(soup)
            self.site_data['links'] = self._extract_important_links(soup)
            
            return True
            
        except Exception as e:
            print(f"Error analyzing website: {str(e)}")
            return False
    
    def _extract_title(self, soup):
        """Extract site title"""
        # Try different methods to get the title
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
            
        return self.domain
    
    def _extract_description(self, soup):
        """Extract site description"""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc.get('content').strip()
        
        # Try og:description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc.get('content').strip()
        
        # Try first paragraph
        first_p = soup.find('p')
        if first_p:
            text = first_p.get_text().strip()
            if len(text) > 50:
                return text[:200] + "..." if len(text) > 200 else text
        
        return f"Website content from {self.domain}"
    
    def _extract_important_links(self, soup):
        """Extract important links from the website"""
        links = {}
        
        # Find navigation links
        nav_links = self._find_navigation_links(soup)
        if nav_links:
            links['Navigation'] = nav_links
        
        # Find documentation links
        doc_links = self._find_documentation_links(soup)
        if doc_links:
            links['Documentation'] = doc_links
        
        # Find API links
        api_links = self._find_api_links(soup)
        if api_links:
            links['API'] = api_links
        
        # Find other important links
        other_links = self._find_other_important_links(soup)
        if other_links:
            links['Resources'] = other_links
        
        return links
    
    def _find_navigation_links(self, soup):
        """Find main navigation links"""
        links = []
        
        # Look for nav elements
        nav_elements = soup.find_all(['nav', 'header'])
        for nav in nav_elements:
            nav_links = nav.find_all('a', href=True)
            for link in nav_links[:5]:  # Limit to first 5
                href = link.get('href')
                text = link.get_text().strip()
                if href and text and len(text) > 1:
                    full_url = urljoin(self.url, href)
                    if self._is_internal_link(full_url):
                        links.append({'text': text, 'url': full_url})
        
        return links[:5]  # Return top 5
    
    def _find_documentation_links(self, soup):
        """Find documentation related links"""
        links = []
        doc_keywords = ['docs', 'documentation', 'guide', 'tutorial', 'help', 'manual']
        
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href')
            text = link.get_text().strip().lower()
            
            if any(keyword in text or keyword in href.lower() for keyword in doc_keywords):
                full_url = urljoin(self.url, href)
                if self._is_internal_link(full_url):
                    links.append({'text': link.get_text().strip(), 'url': full_url})
        
        return links[:3]  # Return top 3
    
    def _find_api_links(self, soup):
        """Find API related links"""
        links = []
        api_keywords = ['api', 'reference', 'endpoint', 'swagger', 'openapi']
        
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href')
            text = link.get_text().strip().lower()
            
            if any(keyword in text or keyword in href.lower() for keyword in api_keywords):
                full_url = urljoin(self.url, href)
                if self._is_internal_link(full_url):
                    links.append({'text': link.get_text().strip(), 'url': full_url})
        
        return links[:3]  # Return top 3
    
    def _find_other_important_links(self, soup):
        """Find other important links"""
        links = []
        important_keywords = ['about', 'contact', 'blog', 'news', 'support', 'faq']
        
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href')
            text = link.get_text().strip().lower()
            
            if any(keyword in text or keyword in href.lower() for keyword in important_keywords):
                full_url = urljoin(self.url, href)
                if self._is_internal_link(full_url):
                    links.append({'text': link.get_text().strip(), 'url': full_url})
        
        return links[:3]  # Return top 3
    
    def _is_internal_link(self, url):
        """Check if link is internal to the domain"""
        try:
            parsed_url = urlparse(url)
            return parsed_url.netloc == self.domain or parsed_url.netloc == ''
        except:
            return False
    
    def generate_llms_txt(self):
        """Generate the llms.txt content"""
        if not self.site_data:
            return None
        
        content = []
        
        # H1 title (required)
        content.append(f"# {self.site_data['title']}")
        content.append("")
        
        # Blockquote description
        if self.site_data.get('description'):
            content.append(f"> {self.site_data['description']}")
            content.append("")
        
        # Add sections for different types of links
        for section_name, links in self.site_data.get('links', {}).items():
            if links:
                content.append(f"## {section_name}")
                content.append("")
                
                for link in links:
                    if link.get('text') and link.get('url'):
                        content.append(f"- [{link['text']}]({link['url']})")
                
                content.append("")
        
        return "\n".join(content)

@llms_bp.route('/analyze', methods=['POST'])
@cross_origin()
def analyze_url():
    """Analyze a URL and return extracted information"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        generator = LLMSGenerator(url)
        
        if generator.analyze_website():
            return jsonify({
                'success': True,
                'data': generator.site_data
            })
        else:
            return jsonify({'error': 'Failed to analyze website'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@llms_bp.route('/generate', methods=['POST'])
@cross_origin()
def generate_llms_txt():
    """Generate llms.txt content"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        generator = LLMSGenerator(url)
        
        if generator.analyze_website():
            llms_content = generator.generate_llms_txt()
            
            if llms_content:
                return jsonify({
                    'success': True,
                    'content': llms_content
                })
            else:
                return jsonify({'error': 'Failed to generate llms.txt content'}), 500
        else:
            return jsonify({'error': 'Failed to analyze website'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@llms_bp.route('/download', methods=['POST'])
@cross_origin()
def download_llms_txt():
    """Download the generated llms.txt file"""
    try:
        data = request.get_json()
        content = data.get('content')
        filename = data.get('filename', 'llms.txt')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        temp_file.write(content)
        temp_file.close()
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

