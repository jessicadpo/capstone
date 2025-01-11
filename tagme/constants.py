"""
Module for storing values that shouldn't change throughout development (e.g., initial list of blacklisted words)
"""
GLOBAL_BLACKLIST = ['apeshit', 'arse', 'arsehole', 'ass', 'asshole', 'assmunch', 'ball gag', 'ball gravy', 'ball licking',
                    'ball sack', 'ball sucking', 'bangbros', 'bitch', 'bitches', 'black cock', 'blowjob', 'blow job',
                    'blow your load', 'bollocks', 'bullshit', 'clusterfuck', 'cum', 'cumming', 'cunt', 'eat my ass',
                    'faggot', 'faggots', 'fuck', 'fucks', 'fucked', 'fucker', 'fuckers', 'fuckin', 'fucking',
                    'fucktards', 'fucko', 'fuckos', 'god damn', 'goddamn', 'motherfucker', 'motherfuckers',
                    'motherfucking', 'negro', 'nigga', 'nigger', 'nig nog', 'piece of shit',  'poon', 'poontang',
                    'retard', 'retards', 'retarded', 'shit', 'shitblimp', 'shits', 'shitter', 'shitting', 'shitty',
                    'slut', 'sluts', 'sodomize', 'sodomy', 'tranny',  'whore']

REWARD_LIST = {
    "New to the Family": "#B52801",         # Red
    "Busy Bee": "#C67A2A",                  # Gold
    "Keen Cataloguer": "#537A00",           # Green
    "Sharp Sorter": "#006996",              # Blue
    "Diligent Documenter": "#C67A2A",       # Gold
    "Elite Archivist": "#B63200",           # Orange
    "Metadata Master": "#820096",           # Purple
}

SEARCH_TYPES = (
    ("Keyword", "Keyword"),
    ("Tag", "Tag"),
    ("Title", "Title"),
    ("Author", "Author"),
    ("Subject", "Subject")
)

SORT_OPTIONS = (
    ("title_az", "Title (A to Z)"),
    ("title_za", "Title (Z to A)"),
    ("author_az", "Author (A to Z)"),
    ("author_za", "Author (Z to A)"),
    ("pubdate_no", "Date Published (Newest to Oldest)"),
    ("pubdate_on", "Date Published (Oldest to Newest)"),
    ("pindate_no", "Date Pinned (Newest to Oldest)"),
    ("pindate_on", "Date Pinned (Oldest to Newest)")
)

FILTER_STATES = (
    (-1, "None"),  # -1 is first so that -1/None (unchecked) is default
    (0, "Exclude"),
    (1, "Include")
)
