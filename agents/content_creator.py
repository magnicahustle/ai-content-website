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
    website_dir = "/home/miki/AI/docs"
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
        import random
        articles = [
            {
                "title": "The Ethics of Artificial Intelligence",
                "content": """
Introduction:
As artificial intelligence becomes more sophisticated, it's crucial to consider the ethical implications of its use. This article delves into the moral questions surrounding AI, from algorithmic bias to the potential for autonomous decision-making.

Body:
One of the most pressing ethical concerns is algorithmic bias. AI systems learn from data, and if that data reflects existing societal biases, the AI will perpetuate and even amplify them. This can have serious consequences in areas like hiring, criminal justice, and loan applications.

Another major ethical dilemma is the question of accountability. When an autonomous system makes a mistake, who is responsible? Is it the programmer, the owner of the system, or the AI itself? Establishing clear lines of responsibility is essential for building trust in AI.

The development of autonomous weapons also raises profound ethical questions. The prospect of machines making life-or-death decisions without human intervention is a frightening one, and there is a growing movement to ban the development and use of such weapons.

Conclusion:
The ethical challenges of AI are complex and multifaceted. As we continue to develop and integrate AI into our society, it's essential to have a robust public discourse about these issues. By proactively addressing these challenges, we can ensure that AI is developed and used in a way that is beneficial to all of humanity.
"""
            },
            {
                "title": "AI in Healthcare: A Revolution in Medicine",
                "content": """
Introduction:
Artificial intelligence is poised to revolutionize the healthcare industry, from diagnostics and treatment to drug discovery and personalized medicine. This article explores the many ways in which AI is transforming healthcare and improving patient outcomes.

Body:
AI-powered diagnostic tools can analyze medical images like X-rays and MRIs with a level of accuracy that often surpasses human radiologists. This can lead to earlier and more accurate diagnoses of diseases like cancer and Alzheimer's.

In the realm of treatment, AI can help doctors create personalized treatment plans based on a patient's genetic makeup, lifestyle, and other factors. This can lead to more effective treatments with fewer side effects.

AI is also accelerating the process of drug discovery. By analyzing vast datasets of biological and chemical information, AI can identify promising new drug candidates much faster than traditional methods.

Conclusion:
The potential of AI to improve healthcare is immense. From more accurate diagnoses to personalized treatments and faster drug discovery, AI is helping to create a future where healthcare is more effective, efficient, and accessible to all.
"""
            }
        ]
        
        chosen_article = random.choice(articles)
        return f"Title: {chosen_article['title']}\n\n{chosen_article['content']}"


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
