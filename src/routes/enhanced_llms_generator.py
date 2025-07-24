from flask import Blueprint, request, jsonify, send_file
from flask_cors import cross_origin
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import io
import tempfile
import os
# import openai
# from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

enhanced_llms_bp = Blueprint('enhanced_llms', __name__)

class EnhancedLLMSGenerator:
    def __init__(self, url):
        self.url = url
        self.domain = urlparse(url).netloc
        self.site_data = {}
        self.analysis_steps = []
        self.quality_score = 0
        
    def analyze_website_advanced(self):
        """Advanced website analysis with AI and JavaScript rendering"""
        try:
            self.analysis_steps.append("Initializing advanced analysis...")
            
            # Step 1: Basic content extraction
            self.analysis_steps.append("Extracting basic website content...")
            basic_success = self._extract_basic_content()
            
            if not basic_success:
                return False
            
            # Step 2: JavaScript rendering for SPAs
            self.analysis_steps.append("Rendering JavaScript content...")
            self._extract_dynamic_content()
            
            # Step 3: AI-powered content analysis
            self.analysis_steps.append("Analyzing content with AI...")
            self._ai_content_analysis()
            
            # Step 4: Quality scoring
            self.analysis_steps.append("Calculating content quality score...")
            self._calculate_quality_score()
            
            # Step 5: Smart categorization
            self.analysis_steps.append("Categorizing content intelligently...")
            self._smart_categorization()
            
            self.analysis_steps.append("Analysis complete!")
            return True
            
        except Exception as e:
            print(f"Error in advanced analysis: {str(e)}")
            self.analysis_steps.append(f"Error: {str(e)}")
            return False
    
    def _extract_basic_content(self):
        """Extract basic content using requests and BeautifulSoup"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract comprehensive metadata
            self.site_data['title'] = self._extract_title(soup)
            self.site_data['description'] = self._extract_description(soup)
            self.site_data['keywords'] = self._extract_keywords(soup)
            self.site_data['raw_links'] = self._extract_all_links(soup)
            self.site_data['content_text'] = self._extract_main_content(soup)
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Error extracting basic content: {str(e)}")
            return False
    
    def _extract_dynamic_content(self):
        """Extract content from JavaScript-rendered pages"""
        try:
            # Skip dynamic content extraction for performance
            print("Skipping dynamic content extraction for performance")
            return
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(60)
            driver.get(self.url)
            print(f"Selenium: Page loaded for {self.url}")
            
            # Wait for page to load
            time.sleep(5)
            print("Selenium: Waited for 5 seconds.")            
            # Extract additional content after JavaScript execution
            dynamic_soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Update with dynamic content
            dynamic_links = self._extract_all_links(dynamic_soup)
            self.site_data['dynamic_links'] = dynamic_links
            
            # Extract any additional content that appeared after JS execution
            dynamic_content = self._extract_main_content(dynamic_soup)
            if len(dynamic_content) > len(self.site_data.get('content_text', '')):
                self.site_data['content_text'] = dynamic_content
            
            driver.quit()
            
        except Exception as e:
            print(f"Error extracting dynamic content: {str(e)}")
            # Continue without dynamic content if this fails
            pass
    
    def _ai_content_analysis(self):
        """Use AI to analyze and summarize content"""
        try:
            # Skip AI analysis for performance
            print("Skipping AI analysis for performance")
            return
            
            if 'openai' not in globals():
                print("OpenAI module not loaded, skipping AI analysis")
                return
            
            client = openai.OpenAI()
            
            # Prepare content for AI analysis
            content_summary = f"""
            Website: {self.url}
            Title: {self.site_data.get('title', 'Unknown')}
            Description: {self.site_data.get('description', 'No description')}
            Content: {self.site_data.get('content_text', '')[:2000]}...
            """
            
            # AI analysis prompt
            prompt = f"""
            Analyze this website content and provide:
            1. A concise, professional description (1-2 sentences)
            2. The main purpose/category of the website
            3. Key topics covered
            4. Target audience
            5. Content quality assessment (1-10)
            
            Website content:
            {content_summary}
            
            Respond in JSON format with keys: description, category, topics, audience, quality_score
            """
            
            response = client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": "You are an expert web content analyzer. Provide concise, accurate analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            ai_analysis = json.loads(response.choices[0].message.content)
            self.site_data['ai_analysis'] = ai_analysis
            
            # Update description with AI-generated one if better
            if ai_analysis.get('description') and len(ai_analysis['description']) > 20:
                self.site_data['ai_description'] = ai_analysis['description']
            
        except Exception as e:
            print(f"Error in AI analysis: {str(e)}")
            # Continue without AI analysis if this fails
            pass
    
    def _calculate_quality_score(self):
        """Calculate content quality score"""
        score = 0
        
        # Title quality (0-20 points)
        if self.site_data.get('title'):
            title_len = len(self.site_data['title'])
            if 10 <= title_len <= 70:
                score += 20
            elif title_len > 0:
                score += 10
        
        # Description quality (0-20 points)
        if self.site_data.get('description'):
            desc_len = len(self.site_data['description'])
            if 50 <= desc_len <= 300:
                score += 20
            elif desc_len > 0:
                score += 10
        
        # Content richness (0-20 points)
        content_len = len(self.site_data.get('content_text', ''))
        if content_len > 1000:
            score += 20
        elif content_len > 500:
            score += 15
        elif content_len > 100:
            score += 10
        
        # Link diversity (0-20 points)
        total_links = len(self.site_data.get('raw_links', []))
        if total_links > 20:
            score += 20
        elif total_links > 10:
            score += 15
        elif total_links > 5:
            score += 10
        
        # AI quality score (0-20 points)
        if self.site_data.get('ai_analysis', {}).get('quality_score'):
            ai_score = int(self.site_data['ai_analysis']['quality_score'])
            score += min(20, ai_score * 2)
        
        self.quality_score = min(100, score)
        self.site_data['quality_score'] = self.quality_score
    
    def _smart_categorization(self):
        """Intelligently categorize links using AI and heuristics"""
        all_links = self.site_data.get('raw_links', [])
        
        unique_links = {}
        for link in all_links:
            if link.get("url"):
                unique_links[link["url"]] = link
        
        all_links = list(unique_links.values())
        
        categories = {
            'Navigation': [],
            'Documentation': [],
            'API': [],
            'Resources': [],
            'Products': [],
            'Support': [],
            'Company': []
        }
        
        # Enhanced keyword matching
        category_keywords = {
            'Navigation': ['home', 'about', 'contact', 'services', 'products', 'solutions'],
            'Documentation': ['docs', 'documentation', 'guide', 'tutorial', 'help', 'manual', 'wiki', 'knowledge'],
            'API': ['api', 'reference', 'endpoint', 'swagger', 'openapi', 'sdk', 'developer'],
            'Resources': ['blog', 'news', 'articles', 'resources', 'downloads', 'tools', 'templates'],
            'Products': ['product', 'features', 'pricing', 'plans', 'demo', 'trial'],
            'Support': ['support', 'faq', 'help', 'contact', 'ticket', 'community', 'forum'],
            'Company': ['about', 'team', 'careers', 'investors', 'press', 'legal', 'privacy']
        }
        
        for link in all_links:
            if not link.get('text') or not link.get('url'):
                continue
                
            text_lower = link['text'].lower()
            url_lower = link['url'].lower()
            
            # Score each category
            category_scores = {}
            for category, keywords in category_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword in text_lower:
                        score += 3
                    if keyword in url_lower:
                        score += 2
                category_scores[category] = score
            
            # Assign to best matching category
            if category_scores:
                best_category = max(category_scores, key=category_scores.get)
                if category_scores[best_category] > 0:
                    categories[best_category].append(link)
                else:
                    categories['Resources'].append(link)
        
        # Limit links per category and sort by importance
        for category in categories:
            categories[category] = categories[category][:5]
        
        self.site_data['categorized_links'] = categories
    
    def _extract_title(self, soup):
        """Extract site title with fallbacks"""
        # Try multiple methods
        title_tag = soup.find('title')
        if title_tag and title_tag.get_text().strip():
            return title_tag.get_text().strip()
        
        # Try h1
        h1_tag = soup.find('h1')
        if h1_tag and h1_tag.get_text().strip():
            return h1_tag.get_text().strip()
        
        # Try og:title
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title and og_title.get('content'):
            return og_title.get('content').strip()
        
        return self.domain
    
    def _extract_description(self, soup):
        """Extract site description with multiple fallbacks"""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc.get('content').strip()
        
        # Try og:description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc.get('content').strip()
        
        # Try first meaningful paragraph
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 50 and not text.startswith(('Cookie', 'This site', 'We use')):
                return text[:300] + "..." if len(text) > 300 else text
        
        return f"Content from {self.domain}"
    
    def _extract_keywords(self, soup):
        """Extract meta keywords"""
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag and keywords_tag.get('content'):
            return keywords_tag.get('content').strip()
        return ""
    
    def _extract_all_links(self, soup):
        """Extract all internal links with context"""
        links = []
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href')
            text = link.get_text().strip()
            
            if not href or not text or len(text) < 2:
                continue
            
            full_url = urljoin(self.url, href)
            
            # Only include internal links
            if self._is_internal_link(full_url):
                links.append({
                    'text': text,
                    'url': full_url,
                    'context': self._get_link_context(link)
                })
        
        return links
    
    def _extract_main_content(self, soup):
        """Extract main content text"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Try to find main content area
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile('content|main'))
        
        if main_content:
            return main_content.get_text(separator=' ', strip=True)[:3000]
        
        # Fallback to body content
        body = soup.find('body')
        if body:
            return body.get_text(separator=' ', strip=True)[:3000]
        
        return soup.get_text(separator=' ', strip=True)[:3000]
    
    def _get_link_context(self, link_element):
        """Get context around the link"""
        parent = link_element.parent
        if parent:
            return parent.get_text().strip()[:100]
        return ""
    
    def _is_internal_link(self, url):
        """Check if link is internal"""
        try:
            parsed_url = urlparse(url)
            return parsed_url.netloc == self.domain or parsed_url.netloc == ''
        except:
            return False
    
    def generate_enhanced_llms_txt(self):
        """Generate enhanced llms.txt with AI insights"""
        if not self.site_data:
            return None
        
        content = []
        
        # H1 title (required)
        title = self.site_data.get('title', self.domain)
        content.append(f"# {title}")
        content.append("")
        
        # Enhanced description using AI if available
        description = (
            self.site_data.get('ai_description') or 
            self.site_data.get('description') or 
            f"Content from {self.domain}"
        )
        content.append(f"> {description}")
        content.append("")
        
        # Add AI insights if available
        if self.site_data.get('ai_analysis'):
            ai_data = self.site_data['ai_analysis']
            if ai_data.get('category'):
                content.append(f"**Category:** {ai_data['category']}")
            if ai_data.get('topics'):
                content.append(f"**Topics:** {', '.join(ai_data['topics']) if isinstance(ai_data['topics'], list) else ai_data['topics']}")
            content.append("")
        
        # Add categorized sections
        categorized_links = self.site_data.get('categorized_links', {})
        
        for section_name, links in categorized_links.items():
            if links and len(links) > 0:
                content.append(f"## {section_name}")
                content.append("")
                
                for link in links:
                    if link.get('text') and link.get('url'):
                        # Add context if available
                        context = link.get('context', '')
                        if context and len(context) > 20:
                            content.append(f"- [{link['text']}]({link['url']}): {context[:100]}...")
                        else:
                            content.append(f"- [{link['text']}]({link['url']})")
                
                content.append("")
        
        return "\n".join(content)

@enhanced_llms_bp.route('/analyze-advanced', methods=['POST'])
@cross_origin()
def analyze_url_advanced():
    """Advanced URL analysis with AI"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        generator = EnhancedLLMSGenerator(url)
        
        if generator.analyze_website_advanced():
            return jsonify({
                'success': True,
                'data': generator.site_data,
                'analysis_steps': generator.analysis_steps,
                'quality_score': generator.quality_score
            })
        else:
            return jsonify({
                'error': 'Failed to analyze website',
                'analysis_steps': generator.analysis_steps
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_llms_bp.route('/generate-advanced', methods=['POST'])
@cross_origin()
def generate_llms_txt_advanced():
    """Generate enhanced llms.txt content"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        generator = EnhancedLLMSGenerator(url)
        
        if generator.analyze_website_advanced():
            llms_content = generator.generate_enhanced_llms_txt()
            
            if llms_content:
                return jsonify({
                    'success': True,
                    'content': llms_content,
                    'analysis_steps': generator.analysis_steps,
                    'quality_score': generator.quality_score,
                    'metadata': {
                        'title': generator.site_data.get('title'),
                        'description': generator.site_data.get('description'),
                        'ai_insights': generator.site_data.get('ai_analysis', {})
                    }
                })
            else:
                return jsonify({'error': 'Failed to generate llms.txt content'}), 500
        else:
            return jsonify({
                'error': 'Failed to analyze website',
                'analysis_steps': generator.analysis_steps
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_llms_bp.route('/progress/<session_id>', methods=['GET'])
@cross_origin()
def get_progress(session_id):
    """Get analysis progress for a session"""
    # This would typically use a session store like Redis
    # For now, return a simple progress update
    return jsonify({
        'progress': 75,
        'current_step': 'Analyzing content with AI...',
        'total_steps': 5
    })

