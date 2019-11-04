from LambdaPage import LambdaPage


def get(event):
    path = event['path']
    if path not in [
       '/Medusa.html',
       '/Medusa.js',
       '/aframe.min.js',
    ]:
        return 404
    with open(path, 'r') as f:
        page = f.read()
    return 200, page


def init_lambda_page():
    page = LambdaPage()
    page.add_endpoint("get", "/", get, "text/html")

    return page


def lambda_handler(event, context):
    print("SnakeCharmvr received event: {}".format(event))
    return init_lambda_page().handle_request(event)


###############################################################################

if __name__ == "__main__":
        init_lambda_page().start_local()
