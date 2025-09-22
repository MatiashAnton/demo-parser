import asyncio
import flet as ft
from flet.core.types import FontWeight
from search_module import start_search


async def main(page: ft.Page):
    # result = await fetch_json()
    # print(result)
    title = ft.Text(
        "DICE PARSER",
        text_align=ft.TextAlign.CENTER,
        color="black",
        size=24,
        weight=FontWeight('bold')
    )


    title_container = ft.Container(
        content=ft.Column(
            [
                title,
                ft.Divider()
            ],
            alignment=ft.MainAxisAlignment.CENTER,  # елементи вертикально зверху
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.top_center,  # позиція контейнера на сторінці
        width=page.width,  # займати всю ширину сторінки
        bgcolor='yellow'
    )
    easy_apply = ft.Checkbox(label='Easy Apply', value=False)
    easy_apply_col = ft.Column(
        [
            ft.Text('Easy Apply'),
            easy_apply
        ]
    )

    postdate_np = ft.Radio(label='No Preference' , value='None',)
    postdate_today = ft.Radio(label='Today', value='ONE')
    postdate_last_3 = ft.Radio(label='Last 3 Days', value='THREE')
    postdate_last_7 = ft.Radio(label='Last 7 Days', value='SEVEN')
    posted_date_col = ft.RadioGroup(ft.Column(
        [
            ft.Text('Posted Date'),
            postdate_np,
            postdate_today,
            postdate_last_3,
            postdate_last_7
        ]
    ))

    work_setting_remote = ft.Checkbox(label='Remote', value=False)
    work_setting_hybrid = ft.Checkbox(label='Hybrid', value=False)
    work_setting_onsite = ft.Checkbox(label='On-Site', value=False)
    work_setting_col = ft.Column(
        [
            ft.Text('Work Settings'),
            work_setting_remote,
            work_setting_hybrid,
            work_setting_onsite
        ]
    )

    employment_type_fulltime = ft.Checkbox(label='Full Time', value=False)
    employment_type_parttime = ft.Checkbox(label='Part Time', value=False)
    employment_type_contract = ft.Checkbox(label='Contract', value=False)
    employment_type_thirdparty = ft.Checkbox(label='Third Party', value=False)
    employment_type_internship = ft.Checkbox(label='Internship', value=False)
    employment_type = ft.Column(
        [
            ft.Text('Employment Type'),
            employment_type_fulltime,
            employment_type_parttime,
            employment_type_contract,
            employment_type_thirdparty,
            employment_type_internship
        ]
    )

    distance_np = ft.Radio(label='No Preference' , value='None')
    distance_10 = ft.Radio(label='Up to 10 miles', value='10')
    distance_30 = ft.Radio(label='Up to 30 miles', value='30')
    distance_50 = ft.Radio(label='Up to 50 miles', value='50')
    distance_75 = ft.Radio(label='Up to 75 miles', value='75')
    distance_col = ft.RadioGroup(
        ft.Column(
        [
            ft.Text('Distance'),
            distance_np,
            distance_10,
            distance_30,
            distance_50,
            distance_75
        ]
    ))

    employer_type_direct = ft.Checkbox(label='Direct Hire', value=False)
    employer_type_recruiter = ft.Checkbox(label='Recruiter', value=False)
    employer_type_other = ft.Checkbox(label='other', value=False)
    employer_type = ft.Column(
        [
            ft.Text('Employer Type'),
            employer_type_direct,
            employer_type_recruiter,
            employer_type_other
        ]
    )
    work_auth_check = ft.Checkbox(label='Willing to sponsor', value=False)
    work_auth = ft.Column(
        [
            ft.Text('Work Authorization'),
            work_auth_check
        ]
    )

    t = ft.Text()


    filter_col = ft.Column(
        [
            ft.Text('Filters', weight=FontWeight('bold'), size=20),
            easy_apply_col,
            posted_date_col,
            work_setting_col,
            employment_type,
            distance_col,
            employer_type,
            work_auth,
            # sumbit_button
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )
    filter_container = ft.Container(
        content=filter_col,
        height=600,
        width=300,
        bgcolor='yellow'
    )
    count_vacancies = ft.TextField(hint_text='Count of vacancies', read_only=True)
    search_url = ft.TextField(hint_text='Requested link', read_only=True)
    output = ft.TextField(value="RESULT WILL BE HERE", multiline=True, read_only=True)
    # selectable = True

    def on_click_search():
        parsed_json = asyncio.run(start_search(filters=filters_dict))
        count_vacancies.value = f"Count of vacancies: {parsed_json[0]}"
        search_url.value = parsed_json[1]
        output.value = parsed_json[2]
        print(output.value)

        page.update()


    search_btn = ft.Button(text='Search', on_click=lambda e: on_click_search())
    keyword_job_title = ft.TextField(hint_text='Job Title')
    keyword_location = ft.TextField(hint_text='Location (Ex. Austin, Texas)')
    keywords_row = ft.Row(
        [
            keyword_job_title,
            keyword_location,
            search_btn
        ],
        alignment = ft.MainAxisAlignment.CENTER,  # елементи вертикально зверху
    )

    output_col = ft.Column(
        [
            output
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )
    link_plus_count = ft.Row(
        [
            count_vacancies,
            search_url
        ]
    )
    result_col = ft.Column(
        [
            link_plus_count,
            output_col
        ]
    )
    output_container = ft.Container(
        content=result_col,
        width=1100,
        height=550,
        bgcolor='white',  # для наочності
        border=ft.border.all(1, 'black'),
        padding=10
    )
    keywords_plus_result = ft.Column(
        [
            keywords_row,
            output_container
        ]
    )
    keywords_row_container = ft.Container(
        content=keywords_plus_result,
        alignment=ft.alignment.top_center
    )

    filters_dict = {
        'easy_apply': easy_apply,
        'postdate': posted_date_col,
        'employment_type': {
            'employment_type_fulltime': employment_type_fulltime,
            'employment_type_parttime': employment_type_parttime,
            'employment_type_contract': employment_type_contract,
            'employment_type_thirdparty': employment_type_thirdparty,
            'employment_type_internship': employment_type_internship,
        },
        'employer_type': {
            'employer_type_direct': employer_type_direct,
            'employer_type_recruiter': employer_type_recruiter,
            'employer_type_other': employer_type_other,
        },
        'work_settings': {
            'work_setting_remote': work_setting_remote,
            'work_setting_hybrid': work_setting_hybrid,
            'work_setting_onsite': work_setting_onsite
        },
        'work_auth_check': work_auth_check,
        'distance': distance_col,
        'keyword_job_title': keyword_job_title,
        'keyword_location': keyword_location,
    }





    # search_btn = ft.Button(text='Search', on_click=lambda e: asyncio.run(start_search(filters=filters_dict)))
    searching_layout = ft.Row(
        [
            filter_container,
            keywords_row_container
        ],
        vertical_alignment=ft.CrossAxisAlignment.START
    )

    page.add(
        title_container, searching_layout, t
    )


async def run_app():
    await ft.app_async(target=main, view=ft.AppView.WEB_BROWSER)


if __name__ == '__main__':
    asyncio.run(run_app())

