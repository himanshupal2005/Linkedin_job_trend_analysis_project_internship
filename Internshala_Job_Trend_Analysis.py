from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
driver = webdriver.Chrome()
driver.get('https://internshala.com/internships/data-analytics-internship')
time.sleep(5)

soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()
jobs = []
for card in soup.find_all('div', class_='individual_internship'):
    # Title
    title_tag = card.select_one('h3.job-internship-name a.job-title-href')
    title = title_tag.text.strip() if title_tag else 'Not found'

    # Company
    company_tag = card.select_one('p.company-name')
    company = company_tag.text.strip() if company_tag else 'Not found'

    # Location
    location_tag = card.select_one('div.row-1-item.locations a')
    location = location_tag.text.strip() if location_tag else 'Not found'

    # Stipend
    stipend_tag = card.select_one('span.stipend')
    stipend = stipend_tag.text.strip() if stipend_tag else 'Not disclosed'

    # Skills
    skill_tags = card.select('div.job_skill')
    skills = ', '.join([skill.text.strip() for skill in skill_tags]) if skill_tags else 'Not listed'

    jobs.append({
        'Title': title,
        'Company': company,
        'Location': location,
        'Stipend': stipend,
        'Skills': skills
    })
    df = pd.DataFrame(jobs)
df.to_csv('internshala_data_analytics_jobs.csv', index=False)
print("Scraped", len(jobs), "jobs from Internshala.")
df = pd.read_csv("internshala_data_analytics_jobs.csv")
df.head()
df = df[~((df['Title'] == 'Not found') & (df['Company'] == 'Not found'))]
title_keywords = ['data analyst', 'data analytics', 'business analyst', 'data science']
skill_keywords = ['python', 'sql', 'data analytics', 'data science']

df_filtered = df[
    df['Title'].str.lower().str.contains('|'.join(title_keywords)) |
    df['Skills'].str.lower().str.contains('|'.join(skill_keywords))
]
df_filtered.head()
print("Total jobs scraped:", len(df_filtered))
df_filtered.isnull().sum()
df_filtered.duplicated().sum()
top_locations = df['Location'].value_counts().head(5)
print(top_locations)
import matplotlib.pyplot as plt
top_locations.plot(kind='pie', startangle=140)
plt.title('Top 5 Job Locations')
plt.show()
from collections import Counter

all_skills = ','.join(df['Skills'].dropna()).lower().split(',')
skill_counts = Counter([skill.strip() for skill in all_skills if skill.strip()])
top_skills = skill_counts.most_common(10)
skill_df = pd.DataFrame(top_skills, columns=['Skill', 'Count'])
print(skill_df)
plt.figure(figsize=(10, 6))
plt.barh(skill_df['Skill'], skill_df['Count'], color='mediumslateblue')
plt.xlabel('Frequency')
plt.title('Top 10 In-Demand Skills in Data Analyst Internships')
plt.gca().invert_yaxis()  # Highest skill at top
plt.tight_layout()
plt.show()
import re

def extract_stipend(stipend_str):
    match = re.search(r'₹\s*([\d,]+)', stipend_str)
    if match:
        return int(match.group(1).replace(',', ''))
    else:
        return None  # Skip "Competitive stipend" or "Not disclosed"

df['Stipend_numeric'] = df['Stipend'].apply(extract_stipend)
plt.figure(figsize=(10, 6))
df['Stipend_numeric'].dropna().plot(kind='hist',edgecolor='black', bins=10, color='mediumslateblue')
plt.title('Stipend Distribution for Data Analyst Internships')
plt.xlabel('Monthly Stipend (₹)')
plt.ylabel('Number of Internships')
plt.show()
top_job = df.loc[df['Stipend_numeric'].idxmax()]
print("Highest paying internship:")
print(top_job[['Title', 'Company', 'Location', 'Stipend']])