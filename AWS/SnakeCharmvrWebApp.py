from LambdaPage import LambdaPage


def strip_prefix(base, prefix):
    return base[base.startswith(prefix) and len(prefix):]


def get(event):
    print("Received Event: {}".format(event))
    path = event['path']
    if path == '/':
        return 404
    p1 = '/snakecharmvr/'
    p2 = "/"
    path = strip_prefix(strip_prefix(path, p1), p2)
    print(f"Opening {path}")
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
