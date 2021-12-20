import os

def search(dirname):
    filenames = os.listdir(dirname)
    result = []
    for filename in filenames:
      result.append(''.join(["../static/images/",filename]))
    print(result)
    return(result)

