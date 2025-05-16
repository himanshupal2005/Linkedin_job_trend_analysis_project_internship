
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
from urllib.parse import quote_plus

# Setup WebDriver
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

# User Input
job_title = input("Enter job title (e.g., data analyst): ").strip()
location = input("Enter city (e.g., bangalore): ").strip()

# Scrape Naukri job listings
def scrape_jobs(job_title, location, pages=5):
    job_data = []
    driver = get_driver()
    wait = WebDriverWait(driver, 10)

    job_title_encoded = quote_plus(job_title)
    location_encoded = quote_plus(location)

    for page in range(1, pages + 1):
        url = f"https://www.naukri.com/{job_title_encoded}-jobs-in-{location_encoded}?k={job_title_encoded}&l={location_encoded}&pageNo={page}"
        driver.get(url)

        try:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article.jobTuple')))
        except:
            print(f"No job listings found on page {page}")
            continue

        job_cards = driver.find_elements(By.CSS_SELECTOR, 'article.jobTuple')

        for job in job_cards:
            try:
                title = job.find_element(By.CSS_SELECTOR, 'a.title').text.strip()
                company = job.find_element(By.CSS_SELECTOR, 'a.subTitle').text.strip()
                loc = job.find_element(By.CSS_SELECTOR, 'li.location span').text.strip()

                try:
                    skills_elements = job.find_elements(By.CSS_SELECTOR, 'ul.tags li')
                    skills = ', '.join([s.text.strip() for s in skills_elements if s.text.strip()])
                except:
                    skills = ''

                job_data.append({
                    'Job Title': title,
                    'Company': company,
                    'Location': loc,
                    'Skills': skills
                })
            except Exception as e:
                print(f"Skipped job due to error: {e}")
                continue

    driver.quit()
    return pd.DataFrame(job_data)


# Scrape and save
df_jobs = scrape_jobs(job_title, location, pages=5)

if df_jobs.empty:
    print("No jobs found.")
else:
    df_jobs.to_excel(f'job_trend_data_{location}.xlsx', index=False)
    print(f"\n Scraped {len(df_jobs)} jobs. Saved to 'job_trend_data_{location}.xlsx'")

    # Data analysis

    df = df_jobs.copy()
    df['Skills'] = df['Skills'].fillna('').str.lower()
    df['Skill List'] = df['Skills'].apply(lambda x: [skill.strip() for skill in x.split(',') if skill.strip()])

    skills_df = df.explode('Skill List')
    skill_counts = skills_df['Skill List'].value_counts().reset_index()
    skill_counts.columns = ['Skill', 'Count']

    print("\n🔥 Top 10 In-Demand Skills:")
    print(skill_counts.head(10))

    # Bar Chart
    plt.figure(figsize=(12, 6))
    sns.barplot(data=skill_counts.head(10), x='Skill', y='Count', palette='rocket')
    plt.xticks(rotation=45)
    plt.title('Top 10 In-Demand Skills')
    plt.xlabel('Skill')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.show()

    # Heatmap
    skill_matrix = df.explode('Skill List').groupby(['Job Title', 'Skill List']).size().unstack(fill_value=0)
    plt.figure(figsize=(14, 10))
    sns.heatmap(skill_matrix.T, cmap='YlGnBu')
    plt.title('Skill Demand by Job Title')
    plt.xlabel('Job Title')
    plt.ylabel('Skill')
    plt.tight_layout()
    plt.show()
