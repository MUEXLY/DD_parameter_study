def function_with_args(*args):
    for arg in args:
        print(arg)

function_with_args(1, 2, 3, 'four')

def function_with_kwargs(**kwargs):
    for key, value in kwargs.items():
        print(f"{key} = {value}")

function_with_kwargs(a=1, b=2, c='three')

def function_with_both(*args, **kwargs):
    print("Args:", args)
    print("Kwargs:", kwargs)

function_with_both(1, 2, 3, a='one', b='two')

