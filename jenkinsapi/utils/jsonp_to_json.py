def jsonp_to_json(jsonp):
    try:
        l_index = jsonp.index('(') + 1
        r_index = jsonp.rindex(')')
    except ValueError:
        print("Input is not in a jsonp format.")
        return

    res = jsonp[l_index:r_index]
    return res
