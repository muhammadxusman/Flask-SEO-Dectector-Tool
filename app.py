from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import json

app = Flask(__name__)

def analyze_seo(url):

    seo_score = 100
    suggestions = []

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return {"score": 0, "suggestions": ["Website not reachable. Check the URL."]}

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1️⃣ Title Tag
        title_tag = soup.title
        if not title_tag or not title_tag.text.strip():
            seo_score -= 10
            suggestions.append("Missing <title> tag. Add a unique, descriptive title.")
        elif len(title_tag.text.strip()) > 60:
            seo_score -= 5
            suggestions.append("Title is too long (over 60 characters). Shorten it.")

        # 2️⃣ Meta Description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if not meta_desc or not meta_desc.get("content"):
            seo_score -= 10
            suggestions.append("Missing <meta name='description'>. Add a description between 50-160 characters.")

        # 3️⃣ H1 Tag Check
        h1_tags = soup.find_all("h1")
        if len(h1_tags) == 0:
            seo_score -= 10
            suggestions.append("No <h1> tag found. Use an <h1> for the main heading.")

        # 4️⃣ Image Alt Attributes
        images = soup.find_all("img")
        missing_alt = [img for img in images if not img.get("alt")]
        if missing_alt:
            seo_score -= 5
            suggestions.append(f"{len(missing_alt)} images are missing 'alt' attributes. Add descriptive alt text.")

        # 5️⃣ Mobile Friendliness
        viewport_meta = soup.find("meta", {"name": "viewport"})
        if not viewport_meta:
            seo_score -= 5
            suggestions.append("Missing <meta name='viewport'>. Add it for mobile responsiveness.")

        # 6️⃣ HTTPS Check
        if not url.startswith("https://"):
            seo_score -= 10
            suggestions.append("Your website is not secure (missing HTTPS). Get an SSL certificate.")

        # 7️⃣ Robots.txt Check
        robots_txt_url = url.rstrip("/") + "/robots.txt"
        robots_response = requests.get(robots_txt_url, headers=headers)
        if robots_response.status_code != 200:
            seo_score -= 5
            suggestions.append("Missing robots.txt file. Add one to guide search engines.")

        # 8️⃣ Sitemap.xml Check
        sitemap_url = url.rstrip("/") + "/sitemap.xml"
        sitemap_response = requests.get(sitemap_url, headers=headers)
        if sitemap_response.status_code != 200:
            seo_score -= 5
            suggestions.append("Missing sitemap.xml file. Add one for better indexing.")

        # 9️⃣ Structured Data (Schema Markup) Check
        schema_json = soup.find("script", type="application/ld+json")
        if not schema_json:
            seo_score -= 5
            suggestions.append("Missing structured data (Schema.org). Add JSON-LD for better search visibility.")

        # 🔟 Open Graph & Twitter Cards
        og_title = soup.find("meta", property="og:title")
        twitter_title = soup.find("meta", attrs={"name": "twitter:title"})
        if not og_title or not twitter_title:
            seo_score -= 5
            suggestions.append("Missing Open Graph & Twitter Card tags. Add for better social media previews.")

        # 1️⃣1️⃣ Canonical Tag Check
        canonical = soup.find("link", rel="canonical")
        if not canonical:
            seo_score -= 5
            suggestions.append("Missing canonical tag. Add it to prevent duplicate content issues.")

        # 1️⃣2️⃣ Detect Broken Links
        broken_links = []
        for link in soup.find_all("a", href=True):
            try:
                link_url = link["href"]
                if link_url.startswith("/"):
                    link_url = url.rstrip("/") + link_url
                link_response = requests.get(link_url, headers=headers, timeout=5)
                if link_response.status_code == 404:
                    broken_links.append(link_url)
            except:
                pass
        if broken_links:
            seo_score -= 10
            suggestions.append(f"{len(broken_links)} broken links detected. Fix or remove them.")

        # 1️⃣3️⃣ Keyword Density Check
        body_text = soup.get_text().lower()
        words = re.findall(r'\b\w+\b', body_text)
        keyword_freq = {word: words.count(word) for word in set(words)}
        excessive_keywords = [k for k, v in keyword_freq.items() if v > len(words) * 0.05]  # More than 5% density
        if len(excessive_keywords) > 5:
            seo_score -= 10
            suggestions.append("Too many repetitive keywords detected. Avoid keyword stuffing.")

        # 🔥 Final SEO Score
        seo_score = max(seo_score, 0)
        return {"score": seo_score, "suggestions": suggestions}

    except Exception as e:
        return {"score": 0, "suggestions": [f"Error analyzing website: {str(e)}"]}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        website_url = request.form.get("website_url")
        if website_url:
            result = analyze_seo(website_url)
            return jsonify(result)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
