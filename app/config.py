import json
import requests
from bs4 import BeautifulSoup as bs


def get_leetcode_info(username):
    print(username)
    url = f"https://leetcode-api-faisalshohag.vercel.app/{username}"
    try:
        page = requests.get(url)
        page.raise_for_status()
        soap = bs(page.content, "html.parser")
        data = json.loads(soap.text)
        if 'errors' not in data:
            total_solved = data['totalSolved']
            hard_solved = data['hardSolved']
            easy_solved = data['easySolved']
            medium_solved = data['mediumSolved']
            ranking = data['ranking']
            return {
                'total_solved': total_solved,
                'hard_solved': hard_solved,
                'easy_solved': easy_solved,
                'medium_solved': medium_solved,
                'ranking': ranking
            }
        else:
            return "User not found"
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"


LEETCODE_API_ENDPOINT = 'https://leetcode.com/graphql'
DAILY_CODING_CHALLENGE_QUERY = '''
query questionOfToday {
    activeDailyCodingChallengeQuestion {
        date
        userStatus
        link
        question {
            acRate
            difficulty
            freqBar
            frontendQuestionId: questionFrontendId
            isFavor
            paidOnly: isPaidOnly
            status
            title
            titleSlug
            hasVideoSolution
            hasSolution
            topicTags {
                name
                id
                slug
            }
        }
    }
}
'''


def fetch_daily_coding_challenge():
    headers = {'Content-Type': 'application/json'}
    data = {'query': DAILY_CODING_CHALLENGE_QUERY}

    response = requests.post(LEETCODE_API_ENDPOINT, headers=headers, json=data).json()
    title = response['data']['activeDailyCodingChallengeQuestion']['question']['title']
    return str(title).replace(" ", "-").replace("'", "")


def get_problem_details(problem_slug):
    data = {
        "operationName": "questionData",
        "variables": {"titleSlug": problem_slug},
        "query": "query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    boundTopicId\n    title\n    titleSlug\n    content\n    translatedTitle\n    translatedContent\n    isPaidOnly\n    difficulty\n    likes\n    dislikes\n    isLiked\n    similarQuestions\n    contributors {\n      username\n      profileUrl\n      avatarUrl\n      __typename\n    }\n    langToValidPlayground\n    topicTags {\n      name\n      slug\n      translatedName\n      __typename\n    }\n    companyTagStats\n    codeSnippets {\n      lang\n      langSlug\n      code\n      __typename\n    }\n    stats\n    hints\n    solution {\n      id\n      canSeeDetail\n      __typename\n    }\n    status\n    sampleTestCase\n    metaData\n    judgerAvailable\n    judgeType\n    mysqlSchemas\n    enableRunCode\n    enableTestMode\n    envInfo\n    libraryUrl\n    __typename\n  }\n}\n"
    }
    print(problem_slug)
    r = requests.post('https://leetcode.com/graphql', json=data).json()
    soup = bs(r['data']['question']['content'], 'lxml')
    title = r['data']['question']['title']
    question = soup.get_text().replace('\n', ' ')
    related_topics = [tag['name'] for tag in r['data']['question']['topicTags']]

    return [title, question, related_topics]
