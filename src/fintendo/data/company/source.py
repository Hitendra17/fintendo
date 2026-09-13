from fintendo.data.company.models import CompanyProfile


def get_company_source_url(profile: CompanyProfile) -> str:
    if profile.investor_relations_url:
        return str(profile.investor_relations_url)

    return str(profile.official_website)