#!/usr/bin/env python3
import os
import datetime
import re
from bs4 import BeautifulSoup

def main():
    """
    Generates a piece of content and saves it to a file.
    """
    content_dir = "/home/miki/AI/content"
    logs_dir = "/home/miki/AI/logs"
    website_dir = "/home/miki/AI/website"
    articles_dir = os.path.join(website_dir, "articles")
    
    # Create directories if they don't exist
    if not os.path.exists(content_dir):
        os.makedirs(content_dir)

    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    if not os.path.exists(articles_dir):
        os.makedirs(articles_dir)

    # Read the article template
    with open(os.path.join(website_dir, "article_template.html"), "r") as f:
        article_template = f.read()

    def generate_article_content():
        # This function will eventually be replaced by an LLM call or web search
        # For now, it returns a sample article.
        return """
Title: The Future of AI in Everyday Life

Introduction:
Artificial intelligence (AI) is no longer a futuristic concept; it's an integral part of our daily lives, constantly evolving and expanding its reach. From personalized recommendations to advanced medical diagnostics, AI's influence is pervasive. This article explores the exciting prospects of AI's continued integration into our routines and the potential transformations it promises.

Body:
One of the most significant areas where AI is set to make further inroads is in personal assistance. Imagine AI systems that not only manage your schedule but also anticipate your needs, proactively suggest solutions, and seamlessly integrate with all your devices to create a truly intelligent environment. These systems will learn from your habits, preferences, and even your mood to offer unparalleled support.

Healthcare is another sector poised for a revolution. AI-powered diagnostics can analyze medical images and patient data with incredible accuracy, often surpassing human capabilities in early disease detection. Furthermore, AI can personalize treatment plans, predict patient responses to medication, and even assist in drug discovery, leading to more effective and tailored medical care.

In the realm of transportation, autonomous vehicles are just the beginning. AI will optimize traffic flow in smart cities, manage complex logistics for delivery services, and even enhance public transport systems to be more efficient and responsive to demand. This will lead to reduced congestion, lower emissions, and safer travel for everyone.

Conclusion:
The future of AI in everyday life is bright and full of potential. While challenges such as ethical considerations and data privacy need to be addressed, the benefits of AI in enhancing convenience, improving health, and optimizing our environment are undeniable. As AI continues to advance, it will undoubtedly reshape our world in ways we are only just beginning to imagine.
"""

    # Generate content
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_article_content = generate_article_content()
    
    # Extract title and body
    title_match = re.search(r"Title: (.*)", raw_article_content)
    article_title = title_match.group(1).strip() if title_match else f"AI Generated Article {timestamp}"
    article_body = re.sub(r"Title: .*\n\n", "", raw_article_content, 1).strip()
    
    # Process article body for better HTML formatting
    processed_body = []
    sections = re.split(r"(Introduction:|Body:|Conclusion:)", article_body)
    
    # The split will result in an array like ['', 'Introduction:', '...', 'Body:', '...', 'Conclusion:', '...']
    # We need to iterate through it and pair the section titles with their content
    i = 0
    while i < len(sections):
        section_title = sections[i].strip()
        if section_title in ["Introduction:", "Body:", "Conclusion:"]:
            processed_body.append(f"<h3>{section_title}</h3>")
            i += 1
            if i < len(sections):
                content = sections[i].strip()
                paragraphs = content.split('\n\n')
                for p in paragraphs:
                    if p.strip():
                        processed_body.append(f"<p>{p.strip()}</p>")
        elif section_title: # Handle any leading text before the first section title
            paragraphs = section_title.split('\n\n')
            for p in paragraphs:
                if p.strip():
                    processed_body.append(f"<p>{p.strip()}</p>")
        i += 1
    
    html_article_body = "\n".join(processed_body)

    # Populate the template
    formatted_date = datetime.datetime.now().strftime("%B %d, %Y")
    html_content = article_template.replace("{{ article_title }}", article_title)
    html_content = html_content.replace("{{ publish_date }}", formatted_date)
    html_content = html_content.replace("{{ article_body }}", html_article_body)

    # Save HTML article
    article_filename = f"{article_title.replace(' ', '_').lower()}_{timestamp}.html"
    article_path = os.path.join(articles_dir, article_filename)
    with open(article_path, "w") as f:
        f.write(html_content)

    # Update index.html
    index_path = os.path.join(website_dir, "index.html")
    with open(index_path, "r") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    article_list = soup.find(id="article-list")
    if article_list:
        new_li = soup.new_tag("li")
        new_a = soup.new_tag("a", href=f"articles/{article_filename}")
        new_a.string = article_title
        new_li.append(new_a)
        article_list.insert(0, new_li) # Add to the top of the list

    with open(index_path, "w") as f:
        f.write(str(soup))

    # Log action
    log_path = os.path.join(logs_dir, "content_creator.log")
    with open(log_path, "a") as f:
        f.write(f"{datetime.datetime.now()}: Generated HTML article '{article_title}' at '{article_path}' and updated index.html\n")

if __name__ == "__main__":
    main()
