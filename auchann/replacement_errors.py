from typing import Optional

articles = ['de', 'het', 'een']
pronouns = ['dit', 'dat', 'deze', 'die', 'het', 'zulke', 'degene', 'datgene',
            'wie', 'wat', 'welke',
            'ik', 'mij', 'mijn', "m'n", 'me', 'zich',
            'hij', 'hem', 'zijn', "z'n",
            'zij', 'haar',
            'wij', 'we',
            'ons', 'onze',
            'jij', 'je', 'u', 'julie',
            'hun', 'hen', 'ze']
prepositions = ['aan', 'achter', 'af', 'behalve', 'beneden', 'bij', 'binnen', 'boven', 'buiten', 'door', 'in', 'langs', 'met', 'na', 'naar',
                'naast', 'om', 'onder', 'op', 'over', 'per', 'sinds', 'te', 'tegen', 'tot', 'tussen', 'uit', 'van', 'via', 'volgens', 'voor', 'zonder',
                'erop', 'eraf']


def detect_error(original: str, correction: str) -> Optional[str]:
    if original == correction:
        return None

    if original in articles and correction in articles:
        return 's:r:gc:art'

    if original in pronouns and correction in pronouns:
        return 's:r:gc:pro'

    if original in prepositions and correction in prepositions:
        return 's:r:prep'
