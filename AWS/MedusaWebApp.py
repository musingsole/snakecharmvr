from LambdaPage import LambdaPage
from bs4 import BeautifulSoup
from DDBMemory import DDBMemory, Memory
from markdown import markdown as markdown_to_html

###############################################################################


snakecharmvr_mem = DDBMemory(tablename="snakecharmvrwebapptable")


def get_home_page(event=None):
    with open("homepage.md", "r") as f:
        homepage_md = f.read()
    homepage_html = markdown_to_html(homepage_md)

    return homepage_html


def retrieve_entry_page(entry_title):
    try:
        print("Recovering memory")
        memories = snakecharmvr_mem.remember("entry_title", trunk=entry_title)
    except Exception as e:
        print("Failed: {}".format(e))
        memories = []
    finally:
        if not memories:
            return 404, "Failed to locate {}".format(entry_title)
        else:
            print("Formatting building entry page")
            page = memories[0]['PAGE']
            soup = BeautifulSoup(page, 'html.parser')
            return 200, str(soup)


def get(event):
    if event['queryStringParameters'] and 'entry_title' in event['queryStringParameters']:
        print("Retrieving {}".format(event['queryStringParameters']['entry_title']))
        entry_title = event['queryStringParameters']['entry_title']
    else:
        return 200, get_home_page()

    print("Building page")
    return retrieve_entry_page(entry_title)


def post(event):
    try:
        entry_title = event['queryStringParameters']['entry_title']
        page = event['body']
    except Exception as e:
        print("Failed to process post: {}".format(e))
        return 302, get_home_page()

    return retrieve_entry_page(entry_title)

    # Write to DDB
    try:
        memory = Memory(**{
            "ROOT": "entry_title",
            "BRANCH": entry_title,
            "PAGE": page
        })
        snakecharmvr_mem.memorize([memory], identifier="{}_write".fromat(entry_title))
    except Exception as e:
        print("Failed to store {}".format(entry_title))
        return 502, "Failed to write entry {}".format(entry_title)

    # Return new page
    return retrieve_entry_page(entry_title)


def init_lambda_page():
    page = LambdaPage()
    page.add_endpoint("get", "/", get, "text/html")
    page.add_endpoint("post", "/", post, "text/html")

    return page


def lambda_handler(event, context):
    print("SnakeCharmvr received event: {}".format(event))
    return init_lambda_page().handle_request(event)


###############################################################################

if __name__ == "__main__":
        init_lambda_page().start_local()
