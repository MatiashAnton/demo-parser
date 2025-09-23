import aiohttp
from bs4 import BeautifulSoup
import json
import asyncio
from semantic_filtering import validate_results


def parse_filters(filters: dict) -> tuple[dict, str]:
    ready_filters = {}
    request_keywords = ''
    for filter_k, filter_v in filters.items():
        match filter_k:
            case 'easy_apply':
                if filter_v.value is True:
                    ready_filters['easy_apply'] = 'filters.easyApply=true'
            case 'postdate':
                if filter_v.value is not None and 'None' not in filter_v.value:
                    ready_filters['postdate'] = f'filters.postedDate={filter_v.value}'
            case 'work_settings':
                work_values = ''
                if any(True for v in filter_v.values() if v.value is True):
                    work_values += 'filters.workplaceTypes='
                    for i, (k, v) in enumerate(filter_v.items()):
                        k, v = (k, v)
                        if k == 'work_setting_remote' and v.value is True:
                            work_values += 'Remote'
                            work_values += '|'
                        if k == 'work_setting_hybrid' and v.value is True:
                            work_values += 'Hybrid'
                            work_values += '|'
                        if k == 'work_setting_onsite' and v.value is True:
                            work_values += 'On-Site'
                            work_values += '|'
                    ready_filters['work_settings'] = work_values[:-1]
            case 'employment_type':
                employment_values = ''
                if any(True for v in filter_v.values() if v.value is True):
                    employment_values += 'filters.employmentType='
                    for i, (k, v) in enumerate(filter_v.items()):
                        k, v = (k, v)
                        if k == 'employment_type_fulltime' and v.value is True:
                            employment_values += 'FULLTIME'
                            employment_values += '|'
                        elif k == 'employment_type_parttime' and v.value is True:
                            employment_values += 'PARTTIME'
                            employment_values += '|'
                        elif k == 'employment_type_contract' and v.value is True:
                            employment_values += 'CONTRACTS'
                            employment_values += '|'
                        elif k == 'employment_type_thirdparty' and v.value is True:
                            employment_values += 'THIRD_PARTY'
                            employment_values += '|'
                        elif k == 'employment_type_internship' and v.value is True:
                            employment_values += 'INTERNSHIP'
                            employment_values += '|'
                    ready_filters['employment_type'] = employment_values[:-1]
            case 'distance':
                if filter_v.value is not None and 'None' not in filter_v.value:
                    ready_filters['distance'] = f'radius={filter_v.value}'
            case 'employer_type':
                work_values = ''
                if any(True for v in filter_v.values() if v.value is True):
                    work_values += 'filters.employerType='
                    for i, (k, v) in enumerate(filter_v.items()):
                        k, v = (k, v)
                        if k == 'employer_type_direct' and v.value is True:
                            work_values += 'Direct+Hire'
                            work_values += '|'
                        if k == 'employer_type_recruiter' and v.value is True:
                            work_values += 'Recruiter'
                            work_values += '|'
                        if k == 'employer_type_other' and v.value is True:
                            work_values += 'Other'
                            work_values += '|'
                    ready_filters['employer_type'] = work_values[:-1]
            case 'work_auth_check':
                if filter_v.value is True:
                    ready_filters['work_auth_check'] = 'filters.willingToSponsor=true'
            case 'keyword_job_title':
                if filter_v.value != '':
                    ready_filters['keyword_job_title'] = f"q={filter_v.value.replace(' ', '+')}"
                    request_keywords = filter_v.value
            case 'keyword_location':
                if filter_v.value != '':
                    ready_filters['keyword_location'] = f"location={filter_v.value.replace(' ', '+')}"

    return ready_filters, request_keywords


def create_link(filters: dict) -> str:
    url = 'https://www.dice.com/jobs?'
    for k, v in filters.items():
        url += v
        url += '&'
    url = url[:-1]
    return url


def parse_request_result(data):
    print('START PARSING')
    soup = BeautifulSoup(data, 'lxml')
    scripts = soup.find_all('script')
    for script in scripts:
        script_txt = script.text
        if 'jobList' in script_txt:
            start = script_txt.find('"jobList') + 11
            end = script_txt.rfind('"meta') - 2
            raw_json = script_txt[start:end] + '}'

            # роздекодувати escape-послідовності (\u0026, \")
            raw_json = raw_json.encode("utf-8").decode("unicode_escape")

            # тепер можна перетворити у Python-словник
            parsed = json.loads(raw_json)
            # print(json.dumps(parsed, indent=2))
            # result = json.dumps(parsed, indent=2)
            return parsed


async def fetch_task(url):
    page = url[-7:]
    if page.startswith('&'):
        page = page[1:]
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            data = await response.text()
            return page, data


async def create_parsing_requests(url: str, pages: str) -> list:
    pages = int(pages)
    tasks = []
    for page in range(2, pages+1):
        page_url = url + f"&page={page}"
        tasks.append(fetch_task(url=page_url))
    return tasks


async def fetch_json(url: str) -> list[list]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            data = await response.text()
    soup = BeautifulSoup(data, 'lxml')
    sections = soup.find_all('section')

    pages = ''
    for section in sections:
        section = str(section)

        if 'Page 1 of' in section:
            pages_section = section
            start = pages_section.find('Page 1 of')
            end = start + 12
            pages_expression = pages_section[start:end]
            if pages_expression.endswith('"'):
                pages_expression = pages_expression.replace('"', '')

            pages = pages_expression[10:]

    all_results = list()
    page_1 = ('page=1', data)
    all_results.append(page_1)
    if len(pages) == 0:
        return all_results

    tasks = await create_parsing_requests(url=url, pages=pages)
    results = await asyncio.gather(*tasks)
    for r in results:
        all_results.append(r)

    return all_results



async def start_search(filters: dict = 1):
    ready_filters, request_query = parse_filters(filters=filters)
    url = create_link(filters=ready_filters)
    print(url)
    # test_link = 'https://www.dice.com/jobs?filters.easyApply=true&filters.postedDate=SEVEN&filters.employmentType=FULLTIME&filters.employerType=Direct+Hire&filters.workplaceTypes=Remote&q=python'
    # test_link_2 = 'https://www.dice.com/jobs?filters.easyApply=true&filters.postedDate=ONE&filters.employmentType=FULLTIME&filters.employerType=Direct+Hire&filters.workplaceTypes=Remote&q=python'
    # test_link_3 = 'https://www.dice.com/jobs?q=python'
    # test_link_project_manager = 'https://www.dice.com/jobs?filters.employmentType=FULLTIME&filters.postedDate=THREE&filters.workplaceTypes=Remote&q=IT+Project+Manager'
    # test_link_4 = 'https://www.dice.com/jobs?q=CHIEF+MARKETING+OFFICER'
    fetch_result = await fetch_json(url=url)
    parsed_jsons = {}
    items_count = 0
    for item in fetch_result:
        data_dict = dict()
        k, raw_data = item
        result = parse_request_result(data=raw_data)
        parsed_jsons[k] = {}
        for ind, element in enumerate(result['data']):
            ind += 1
            data_dict[ind] = element
        parsed_jsons[k]['data'] = data_dict
        items_count += len(result['data'])

    # request_query = 'IT Project Manager'
    relevant_count, validated_results = await validate_results(parsed_results=parsed_jsons, request_query=request_query)
    results = json.dumps(validated_results, indent=2)
    # print(results)
    return items_count, relevant_count, url, results



if __name__ == '__main__':
    asyncio.run(start_search())