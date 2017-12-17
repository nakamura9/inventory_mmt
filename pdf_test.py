from xhtml2pdf import pisa
import requests

# Define your data
sourceHtml = requests.get("http://facebook.com").text
outputFilename = "test.pdf"
# Utility function
def convertHtmlToPdf(sourceHtml, outputFilename):
    # open output file for writing (truncated binary)
    resultFile = open(outputFilename, "w+b")
    # convert HTML to PDF
    pisaStatus = pisa.CreatePDF(
            sourceHtml, # the HTML to convert
            dest=resultFile) # file handle to recieve result
    # close output file
    resultFile.close() # close output file
    # return True on success and False on errors
    return pisaStatus.err

# Main program
if __name__ == "__main__":
    pisa.showLogging()
    convertHtmlToPdf(sourceHtml, outputFilename)