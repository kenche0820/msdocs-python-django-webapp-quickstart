from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os

import logging
import sys

def index(request):
    logging.error('Request for index page received')
    return render(request, 'hello_azure/index.html')

@csrf_exempt
def hello(request):

    import codecs

    if request.method == 'POST':
        name = request.POST.get('name')
        
        logging.basicConfig(
            level=logging.ERROR,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[logging.FileHandler("debug.log"), logging.StreamHandler(sys.stdout)],
        )
        
        from azure.core.credentials import AzureKeyCredential
        from azure.search.documents import SearchClient

        service_endpoint = "https://ken-cog-search-svc.search.windows.net"
        index_name = "sharepoint-index"
        key = "quRm9N9F4y4vGhgZBFvNtRs86VqLugIBVVeyC0drYaAzSeDm86cn"

        credential = AzureKeyCredential(key)
        client = SearchClient(endpoint=service_endpoint, index_name=index_name, credential=credential)
        results = list(
            client.search(
                search_text=name,
                query_type="semantic",
                semantic_configuration_name="ken-semantic-config",
                query_caption="extractive",
            )
        )

        result = results[0]   
        myLink = "<A href='https://setelab.sharepoint.com/Shared%20Documents/Forms/AllItems.aspx?id=%2FShared%20Documents%2Fdocument%2F" + result["metadata_spo_item_name"] + "&parent=%2FShared%20Documents%2Fdocument&p=true&ga=1'>" + result["metadata_spo_item_name"] + "</A>"          
        
        print(result["@search.reranker_score"])
        logging.error(result["@search.reranker_score"])
        
        captions = result["@search.captions"]
        if captions:
            caption = captions[0]
            if caption.highlights:
                print(f"Caption: {caption.highlights}\n")
                myCaption = caption.highlights
            else:
                print(f"Caption: {caption.text}\n")
                myCaption = caption.text





        LANGUAGE = "english"
        SENTENCES_COUNT = 10


        
        url = "https://en.wikipedia.org/wiki/Automatic_summarization"
        parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
        # or for plain text files
        # parser = PlaintextParser.from_file("document.txt", Tokenizer(LANGUAGE))
        # parser = PlaintextParser.from_string("Check this out.", Tokenizer(LANGUAGE))
        stemmer = Stemmer(LANGUAGE)

        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(LANGUAGE)

        tempContent = ""

        for sentence in summarizer(parser.document, SENTENCES_COUNT):
            #print(sentence)
            tempContent += sentence



        tempOutput = "" 
        i = 0        
        for result in results:
            #tempContent = result["content"]    
            #tempContent = tempContent[0:1000]        
            tempOutput = tempOutput + result["metadata_spo_item_name"] + ";;" + str(round(result["@search.reranker_score"],2)) + ";;" + tempContent + ",,"
                        
        myRows = tempOutput.split(",,")      

        myTable = '<!doctype html><head><title>Azure Semantic Search</title><link rel="stylesheet" href="static/bootstrap/css/bootstrap.min.css"><link rel="icon" href="static/favicon.ico"></head>'
        myTable += "<style>table, th, td {border: 1px solid black;border-collapse: collapse;}</style>"        
        myTable += "<TABLE><TH>File Name</TH><TH>Score</TH><TH>Contents</TH>"
        for myRow in myRows:
            myTable += "<TR>"  
            myCells = myRow.split(";;")

            for i in range(len(myCells)):
                if i == 0:
                    myTable += "<TD><A href='https://setelab.sharepoint.com/Shared%20Documents/Forms/AllItems.aspx?id=%2FShared%20Documents%2Fdocument%2F" + myCells[i] + "&parent=%2FShared%20Documents%2Fdocument&p=true&ga=1'>" + myCells[i] + "</A></TD>"                                       
                else:
                    myTable += "<TD>" + myCells[i] + "</TD>"
    
            myTable += "</TR>"    


        with codecs.open("hello_azure/templates/hello_azure/hello.html", 'w', encoding="utf-8") as outfile:     
            outfile.write("<style>.aligncenter{text-align: center;}</style>")
            outfile.write('<div class="px-4 py-3 my-2 text-center">')
            outfile.write('<P class="aligncenter"><img class="d-block mx-auto mb-4" src="static/images/azure-icon.svg" alt="Azure Logo" width="192" height="192"/></P>')
            outfile.write("<P>" + myCaption + "</P>")
            outfile.write("<P>" + myLink + "</P>")
            outfile.write("<P><a href='http://localhost:8000' class='btn btn-primary btn-lg px-4 gap-3'>Back home</a></P>")            
            outfile.write("<P>" + myTable + "</P>")
            outfile.write('</div')
                    
        # [END semantic_ranking]        
        if name is None or name == '':
            logging.error("Request for hello page received with no query or blank nquery -- redirecting")
            return redirect('index')
        else:
            logging.error("Request for hello page received with name=%s" % caption.text)            
            context = {'answer': caption.text }
            return render(request, 'hello_azure/hello.html', context)
    else:
        return redirect('index')





