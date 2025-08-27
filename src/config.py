# Fetcher settings

# URLS
JUST_JOIN_URL = "https://justjoin.it/job-offers/remote?"
DJINNI_URL = "https://djinni.co/jobs/?&employment=remote"
NO_FLUFF_URL = "https://nofluffjobs.com/pl/praca-zdalna/"
PRACUJ_URL = "https://www.pracuj.pl/praca/praca%20zdalna;wm,home-office"
DOU_URL = "https://jobs.dou.ua/vacancies/?remote&"
BULLDOG_URL = "https://bulldogjob.com/companies/jobs/s/city,Remote/"
ROBOTA_UA_URL = "https://robota.ua/zapros/"


# Jooble API settings

JOOBLE_KEYWORDS = "remote"
JOOBLE_LOCATION = "remote"

# radius = search distance in km from 'location'
# 0 = exact location only, larger values = wider area
JOOBLE_RADIUS = 1000

JOOBLE_MIN_SALARY = 0

# "1" = strict (exact match), "2" = default, "3" = fuzzy
JOOBLE_SEARCH_MODE = 1

# limits jobs to those posted in the last N days.
# example: JOOBLE_DATE=7 → jobs from the last week only.
# empty = no limit
JOOBLE_DATE = None


# Headless mode

# use True or False
JUST_JOIN_HEADLESS = True
DJINNI_HEADLESS = True
NO_FLUFF_HEADLESS = True
PRACUJ_HEADLESS = True
DOU_HEADLESS = True
BULLDOG_HEADLESS = True
ROBOTA_UA_HEADLESS = True


# Fetching limitations

DJINNI_MAX_JOBS = 1000
DOU_MAX_JOBS = 1000
BULLDOG_MAX_JOBS = 1000


# Filtration settings

# set a job threshold to not show vacancies under this score
SCORE_THRESHOLD = 0
