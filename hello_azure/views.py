from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os

def index(request):
    print('Request for index page received')
    return render(request, 'hello_azure/index.html')


import logging
import sys


@csrf_exempt
def hello(request):
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
        print(result["@search.reranker_score"])
        logging.error(result["@search.reranker_score"])
        
        captions = result["@search.captions"]
        if captions:
            caption = captions[0]
            if caption.highlights:
                print(f"Caption: {caption.highlights}\n")
                logging.error(f"Caption: {caption.highlights}\n")    
            else:
                print(f"Caption: {caption.text}\n")
                logging.error(f"Caption: {caption.text}\n")    

        fileNames = ""
        for result in results:
            print("{}\n{}\n)".format(result["id"], result["content"]))  
            fileNames = fileNames + "<P>" + result["metadata_spo_item_name"] + "</P>"
        # [END semantic_ranking]
        logging.error(f"fileNames: {fileNames}\n")
        
        if name is None or name == '':
            print("Request for hello page received with no name or blank name -- redirecting")
            return redirect('index')
        else:
            print("Request for hello page received with name=%s" % caption.text)            
            context = {'name': caption.text, 'file': fileNames }
            return render(request, 'hello_azure/hello.html', context)
    else:
        return redirect('index')





