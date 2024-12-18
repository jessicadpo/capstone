"""
Module for storing values that shouldn't change throughout development (e.g., initial list of blacklisted words)
"""
import enum

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


class ValidSearchTypes(enum.Enum):
    """Enum class for the types of searches that can be performed by users"""
    KEYWORD = "Keyword"
    TAG = "Tag"
    TITLE = "Title"
    AUTHOR = "Author"
    SUBJECT = "Subject"
