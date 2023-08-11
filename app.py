import os

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
import logging
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
import csv


app = Flask(__name__)


def scrape_reviews(product_url):
    response = requests.get(product_url)
    flipkart_html = bs(response.content, 'html.parser')
    products = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
    del products[0:3]
    product = products[0]
    productLink = "https://www.flipkart.com" + product.div.div.div.a['href']
    prodRes = requests.get(productLink)
    prodRes.encoding='utf-8'
    prod_html = bs(prodRes.text, "html.parser")

    commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})   
   
    counter = 0
    reviews = []
    for comment in commentboxes:
        if counter < 10:
            try:
                name_element = comment.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0]
                name = name_element.text if name_element else 'No Name'

                rating_element = comment.div.div.div.div
                rating = rating_element.text if rating_element else 'No Rating'

                review_heading_element = comment.div.div.div.find_all('p', {'class': '_2-N8zT'})[0]
                review_heading = review_heading_element.text if review_heading_element else 'No Review Heading'

                comment_element = comment.div.div.find_all('div', {'class': ''})[0].div
                comment_text = comment_element.text if comment_element else 'No Comment'

                mydict = {"Name": name, "Rating": rating, "CommentHead": review_heading, "Comment": comment_text}
                reviews.append(mydict)

                counter += 1
            except Exception as e:
                print("Exception while processing comment: ", e)
        else:
            break
    
    return reviews  # Move this line outside of the loop

@app.route('/', methods=['GET'])
def homePage():
    return render_template("index.html")

@app.route('/review', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            product_Name = request.form['content']
            product_url = flipkart_url
            reviews = scrape_reviews(product_url)

            save_directory = "Reviews/"

            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            csv_file_path = os.path.join(save_directory, f"{product_Name}.csv")

            # Assume `reviews` is a list of dictionaries containing review information

            fieldnames = ["Name", "Rating", "CommentHead", "Comment"]

            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                csv_writer.writeheader()
                csv_writer.writerows(reviews)
            return render_template('reviews.html', reviews=reviews, product_Name=product_Name)
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'
    else:
        return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
