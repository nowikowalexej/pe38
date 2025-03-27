import requests


def get_html(url: str):
    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        },
    )
    response.raise_for_status()
    return response


# print(response.text)
# with open("vacancy.html", "w") as f:
#     f.write(response.text)

from bs4 import BeautifulSoup


def extract_vacancy_data(html):
    soup = BeautifulSoup(html, "html.parser")

    # Проверяем наличие основных элементов
    title_elem = soup.find("h1", {"data-qa": "vacancy-title"})
    if not title_elem:
        raise ValueError("Не удалось найти заголовок вакансии. Проверьте URL и попробуйте снова.")

    title = title_elem.text.strip()

    # Извлечение зарплаты (может быть не указана)
    salary_elem = soup.find("span", {"data-qa": "vacancy-salary-compensation-type-net"})
    salary = salary_elem.text.strip() if salary_elem else "Не указана"

    # Извлечение опыта работы
    experience_elem = soup.find("span", {"data-qa": "vacancy-experience"})
    experience = experience_elem.text.strip() if experience_elem else "Не указан"

    # Извлечение типа занятости и режима работы
    employment_mode_elem = soup.find("p", {"data-qa": "vacancy-view-employment-mode"})
    employment_mode = employment_mode_elem.text.strip() if employment_mode_elem else "Не указан"

    # Извлечение компании
    company_elem = soup.find("a", {"data-qa": "vacancy-company-name"})
    company = company_elem.text.strip() if company_elem else "Не указана"

    # Извлечение местоположения
    location_elem = soup.find("p", {"data-qa": "vacancy-view-location"})
    location = location_elem.text.strip() if location_elem else "Не указано"

    # Извлечение описания вакансии
    description_elem = soup.find("div", {"data-qa": "vacancy-description"})
    if not description_elem:
        raise ValueError("Не удалось найти описание вакансии. Проверьте URL и попробуйте снова.")
    description = description_elem.text.strip()

    # Извлечение ключевых навыков
    skills = [
        skill.text.strip()
        for skill in soup.find_all(
            "div", {"class": "magritte-tag__label___YHV-o_3-0-3"}
        )
    ]

    # Формирование строки в формате Markdown
    markdown = f"""
# {title}

**Компания:** {company}
**Зарплата:** {salary}
**Опыт работы:** {experience}
**Тип занятости и режим работы:** {employment_mode}
**Местоположение:** {location}

## Описание вакансии
{description}

## Ключевые навыки
- {'\n- '.join(skills) if skills else 'Не указаны'}
"""

    return markdown.strip()


# from bs4 import BeautifulSoup

def extract_candidate_data(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Проверяем наличие основных элементов
    name_elem = soup.find('h2', {'data-qa': 'bloko-header-1'})
    if not name_elem:
        raise ValueError("Не удалось найти имя кандидата. Проверьте URL и попробуйте снова.")
    name = name_elem.text.strip()

    gender_age_elem = soup.find('p')
    gender_age = gender_age_elem.text.strip() if gender_age_elem else "Не указано"

    location_elem = soup.find('span', {'data-qa': 'resume-personal-address'})
    location = location_elem.text.strip() if location_elem else "Не указано"

    job_title_elem = soup.find('span', {'data-qa': 'resume-block-title-position'})
    job_title = job_title_elem.text.strip() if job_title_elem else "Не указана"

    job_status_elem = soup.find('span', {'data-qa': 'job-search-status'})
    job_status = job_status_elem.text.strip() if job_status_elem else "Не указан"

    # Извлечение опыта работы
    experience_section = soup.find('div', {'data-qa': 'resume-block-experience'})
    experiences = []
    if experience_section:
        experience_items = experience_section.find_all('div', class_='resume-block-item-gap')
        for item in experience_items:
            period_elem = item.find('div', class_='bloko-column_s-2')
            duration_elem = item.find('div', class_='bloko-text')
            company_elem = item.find('div', class_='bloko-text_strong')
            position_elem = item.find('div', {'data-qa': 'resume-block-experience-position'})
            description_elem = item.find('div', {'data-qa': 'resume-block-experience-description'})

            period = period_elem.text.strip() if period_elem else "Не указан"
            duration = duration_elem.text.strip() if duration_elem else ""
            company = company_elem.text.strip() if company_elem else "Не указана"
            position = position_elem.text.strip() if position_elem else "Не указана"
            description = description_elem.text.strip() if description_elem else "Нет описания"

            if duration:
                period = period.replace(duration, f" ({duration})")

            experiences.append(f"**{period}**\n\n*{company}*\n\n**{position}**\n\n{description}\n")

    # Извлечение ключевых навыков
    skills_section = soup.find('div', {'data-qa': 'skills-table'})
    skills = []
    if skills_section:
        skills = [skill.text.strip() for skill in skills_section.find_all('span', {'data-qa': 'bloko-tag__text'})]

    # Формирование строки в формате Markdown
    markdown = f"# {name}\n\n"
    markdown += f"**{gender_age}**\n\n"
    markdown += f"**Местоположение:** {location}\n\n"
    markdown += f"**Должность:** {job_title}\n\n"
    markdown += f"**Статус:** {job_status}\n\n"
    
    if experiences:
        markdown += "## Опыт работы\n\n"
        for exp in experiences:
            markdown += exp + "\n"
    else:
        markdown += "## Опыт работы\n\nНе указан\n\n"
        
    markdown += "## Ключевые навыки\n\n"
    markdown += ', '.join(skills) if skills else "Не указаны"

    return markdown

def get_candidate_info(url: str):
    response = get_html(url)
    return extract_candidate_data(response.text)

def get_job_description(url: str):
    response = get_html(url)
    return extract_vacancy_data(response.text)
