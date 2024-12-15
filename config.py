
BOT_TOKEN =  '___' #@enjoy_Latoken_bot enjoy_Latoken
# https://t.me/enjoy_Latoken_bot
# API_KEY = '__'
API_KEY = '__'

OPENAI_MODEL = 'gpt-4o'
URL_LATOKEN = 'https://coda.io/@latoken/latoken-talent/latoken-161'
URL_HACKATHON = 'https://deliver.latoken.com/hackathon'
URL_CULTURE = 'https://coda.io/@latoken/latoken-talent/culture-139'

from os.path import abspath, dirname, join
BASE_DIR = dirname(abspath(__file__))
FILES_DIR = join(BASE_DIR, 'files')
DATABASE = join(BASE_DIR, 'dblatoken.db')

LATOKEN = {'name':'LATOKEN','about':'','files': ['What_is_Latoken.txt','about.txt', 'Term_of_use.txt', 'Unsupported.txt', 'What_is_Latoken.txt', 'KYC.txt']}
HACKATHON = {'name':'HACKATHON','about':'хакатоне','files': ['latoken-161.txt', 'hakhathon.txt']}
CULTURE = {'name':'CULTURE','about':'культуре','files': ['culture.txt', 'video.txt', 'culture_princ.txt', 'First_week.txt','Preobrazhenskiy.txt',]}
ALL = {'name':'ALL','about':'','files':[]}

BUTTONS = ['"О компании"', '"Хакатон"', '"Культура"', '"Все категории"']
BTT_CNTX  = {BUTTONS[0]:LATOKEN, BUTTONS[1]:HACKATHON, BUTTONS[2]:CULTURE, BUTTONS[3]:ALL}
NUMBER_ALL = 3

SQL_CRT_MESS = ('CREATE TABLE IF NOT EXISTS mess '
           '(id INTEGER PRIMARY KEY, tlgid INTEGER NOT NULL,text TEXT,cntx TEXT,date DATE);')
SQL_CRT_TEST = ('CREATE TABLE IF NOT EXISTS test '
           '(id INTEGER PRIMARY KEY, tlgid INTEGER NOT NULL,qwst TEXT, '
                'arght TEXT, awrng TEXT, irgh INTEGER, iansw INTEGER, dateqw DATE, datean DATE);')

SQL_VIEW = ("""
CREATE VIEW IF NOT EXISTS user_tests AS
SELECT
tlgid,
COUNT(*) AS total,
SUM(CASE WHEN irgh = iansw THEN 1 ELSE 0 END) AS right,
ROUND(AVG((JULIANDAY(datean) - JULIANDAY(dateqw)) * 86400), 2) AS time
FROM
test
GROUP BY
tlgid;
""")
