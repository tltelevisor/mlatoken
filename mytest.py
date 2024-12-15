import openai
from functools import wraps
from oai import check_openai_api_key
import logging
logging.basicConfig(level=logging.INFO, filename='latoken.log',
                    format='%(asctime)s %(levelname)s %(message)s')

clienttest = 1

def check_openai_api_key(api_key = API_KEY):
    client = openai.OpenAI(api_key=api_key)
    try:
        client.models.list()
    except openai.AuthenticationError as err:
        logging.error(f'err: {err}, api_key: {api_key}')
        return False
    else:
        return True

def uppercase(func):
    @wraps(func)
    def wrapper():
        original_result = func()
        modified_result = original_result.upper()
        return modified_result
    return wrapper

@uppercase
def greet():
    return 'Hello!'

def chk_oai(func):
    oai = False
    if oai:
        return func
    else:
        @wraps(func)
        def wout_oai(*args, **kwargs):
            print(args)
            print(type(args))
            print(kwargs)
            print(type(kwargs))
            newresult = 0 #new_func(*args, **kwargs)
            return newresult
        return wout_oai

def trace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f'TRACE: calling {func.__name__}() '
              f'with {args}, {kwargs}')

        original_result = func(*args, **kwargs)

        print(f'TRACE: {func.__name__}() '
              f'returned {original_result!r}')

        return original_result
    return wrapper
@chk_oai
def test_f(x,y,z,q=10,w=20,e=30):
    print(clienttest)
    return x,y,z,q,w,e

def dec_check_openai_api_key(function):
    try:
        function
    except openai.AuthenticationError:
        return False
    else:
        return True

if __name__ == '__main__':
    # print(greet())
    x = test_f(1,2,3)
    print(x)
    # dec_func(test_f(1))

    # if check_openai_api_key(API_KEY):
    #     print("Valid OpenAI API key.")
    # else:
    #     print("Invalid OpenAI API key.")

