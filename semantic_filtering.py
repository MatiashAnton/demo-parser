from sentence_transformers import SentenceTransformer, util
import asyncio


# завантажуємо модель (скачає автоматично при першому запуску)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


def reorganize_structure(structure: dict) -> dict:
    reorganized = {}
    for page in structure.keys():
        reorganized[page] = {}
        for k, element in structure[page]['data'].items():
            reorganized[page][k] = (page, k, element['title'])
    return reorganized


def validate_structure(original_structure: dict, structure: dict, keywords: str):
    thrashold = 0.80
    vacancies = []
    pages = []
    vacancies_keys = []
    for s in structure.keys():
        for key, element in structure[s].items():
            vacancies_keys.append(key)
            pages.append(element[0])
            vacancies.append(element[2])


    embeddings_vacancies = model.encode(vacancies, convert_to_tensor=True)
    embedding_query = model.encode(keywords, convert_to_tensor=True)
    cosine_scores = util.cos_sim(embedding_query, embeddings_vacancies)[0]
    relevant_count = 0
    for p, k, v, score in zip(pages, vacancies_keys, vacancies, cosine_scores):
        if score < thrashold:
            print(f"{k} / {v} / {score}")
            if k in original_structure[p]['data']:  # ✅ перевірка перед видаленням
                del original_structure[p]['data'][k]

        else:
            print(f"MATCH - {k} / {v} / {score}")
            relevant_count += 1

    return relevant_count, original_structure


async def validate_results(parsed_results: dict, request_query: str):
    structure_to_validate = reorganize_structure(structure=parsed_results)
    validated = validate_structure(original_structure=parsed_results, structure=structure_to_validate, keywords=request_query)
    # print(structure_to_validate)
    return validated
