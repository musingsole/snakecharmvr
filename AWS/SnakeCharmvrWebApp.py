from LambdaPage import LambdaPage


def get(event):
    print("Received Event: {}".format(event))
    path = event['path']
    if path == '/':
        path = '/SnakeCharmvr.html'
    if path not in ['/SnakeCharmvr.html',
                    '/SnakeCharmvr.js',
                    '/aframe.min.js']:
        return 404
    path = path.lstrip('/')
    with open(path, 'r') as f:
        page = f.read()
    return 200, page


def init_lambda_page():
    page = LambdaPage()
    page.add_endpoint("get", "/{proxy+}", get, "text/html")

    return page


def lambda_handler(event, context):
    print("SnakeCharmvr received event: {}".format(event))
    return init_lambda_page().handle_request(event)


###############################################################################

if __name__ == "__main__":
        init_lambda_page().start_local()
