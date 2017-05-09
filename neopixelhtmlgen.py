# Provides functions to provide web content

def header(title):
    output = "<html><head><title>"+title+"</title></head>"
    output += "<body><h1>"+title+"</h1>"
    return output

    
def footer():
    output = "</body></html>"
    return output

def indexPage (sequences):
    return header("NeoPixel controlIndex")+"Test"+footer()