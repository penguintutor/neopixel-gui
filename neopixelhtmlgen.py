# Provides functions to provide web content

def header(title):
    output = """<html>
        <head>
        <title>"""+title+"""</title>
        <!-- uses jpicker colour picker from http://www.digitalmagicpro.com/jPicker/ -->
        <script language="JavaScript" src="public/jquery-3.2.1.slim.min.js"></script>
        <script language="JavaScript" src="public/jpicker-1.1.6/jpicker-1.1.6.min.js"></script>
        </head>"""
    output += "<body>"
    return output

    
def footer():
    output = "</body></html>"
    return output

# Formatted page with list of sequences
def indexPage (sequences):

    body = """
    <h1>NeoPixel control - Index</h1>
    <ul>"""
    for key, value in sequences.items() :
        body+= "<li><a href=\""+"/sequence?seq="+key+"\">"+value+"</a></li>\n"
    body += """</ul>"""
    
    
    body += """<h2>Colour picker</h2>
        <script type="text/javascript">
            $(document).ready(
            function()
            {
            	$('#Expandable').jPicker(
				{
					window:
					{
						expandable: true
					}
				});
            });
        </script>
        <span id="Expandable"></span>
        """
    
    
    return header("NeoPixel control - Index")+body+footer()
