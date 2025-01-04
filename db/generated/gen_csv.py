from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import random
import pandas as pd
import json

# import json with real product data, filtering for products that have images, prices, and descriptions
parsed_beauty = {}
i = 0
with open("meta_All_Beauty.jsonl", 'r') as fp:
    for line in fp:
        data = json.loads(line.strip())
        hasImage = data["images"][0]["hi_res"] is not None
        hasPrice = data["price"] is not None
        if data["description"]:
            if hasImage & hasPrice:                    
                parsed_beauty[i] = data
                i += 1

# import json with real product review data, filtering for ones that have reviews
beauty_reviews = {}
i = 0
with open("All_Beauty.jsonl", 'r') as fr:
    for line in fr:
        data = json.loads(line.strip())
        if data["rating"] is not None:
            beauty_reviews[i] = data
            i += 1

# import txt file with realistic product category names
with open('categories.txt') as f:
    categories = [line.rstrip() for line in f]
num_categories = len(categories)

# prepare seed for random data generation 
random.seed(0)
Faker.seed(0)
fake = Faker('en_US')

# table quantities that are continuously populated and may be used as variables in other tables 
num_accounts = 2000
num_products = 3000

def get_csv_writer(f):
    return csv.writer(f, dialect='unix')

# populate account.csv
# accounts has continuous user_id values in num_accounts
def gen_account(num_accounts):
    with open('Account.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Account...', end=' ', flush=True)
        for user_id in range(num_accounts):
            # Make email unique by appending unique user_id to the end of each user's email
            e_parts = fake.free_email().split('@')
            email = e_parts[0] + str(user_id) + '@' + e_parts[1]
            plain_password = f'pass{user_id}'
            password = generate_password_hash(plain_password)
            full_name = fake.name()
            balance = fake.pydecimal(right_digits=2, positive=True, max_value=9999999.99)
            # Sellers have a user_id that is evenly divisible by 3
            if user_id % 3 == 0:
                is_seller = True
            else:
                is_seller = False
            street_address = fake.street_address()
            city = fake.city()
            state = fake.state_abbr()
            zip_code = fake.zipcode()
            country = 'United States' #fake.country()
            writer.writerow([user_id, email, password, full_name, balance, is_seller, street_address, city, state, zip_code, country])
        print(f'{num_accounts} generated')
    return

# populate cartItem.csv
def gen_cart_item(num_cart_items):
    print('CartItem...', end=' ', flush=True)
    product_listing = pd.read_csv('ProductListing.csv')
    data = []
    for uid in range(num_cart_items):
        user_id = random.randrange(num_accounts)
        # Dependency on product_id and seller_id pairs from ProductListing
        row = random.randrange(product_listing.shape[0])
        listing = product_listing.iloc[row]
        product_id = int(listing.iloc[0])
        seller_id = int(listing.iloc[1])
        # Cart quantity is <= whichever is smaller between 8 and the item's inventory_count
        max_quantity = min(int(listing.iloc[3]), 8)
        # bias quantities towards lower nums
        quantity = int(1 + (max_quantity - 1) * pow(random.random(), 2))
        saved_for_later = fake.pybool()
        data.append([user_id, product_id, seller_id, quantity, saved_for_later])
    # Make primary keysets unique
    df = pd.DataFrame(data, columns=['user_id', 'product_id', 'seller_id', 'quantity', 'saved_for_later'])
    df = df.drop_duplicates(subset=['user_id', 'product_id', 'seller_id'])
    df.to_csv('CartItem.csv', index=False, header=False)
    print(f'{df.shape[0]} of {num_cart_items} uniquely generated')
    return

# populate category.csv
# category has continuous category_id in num_categories
def gen_category(num_categories):
    with open('Category.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Category...', end=' ', flush=True)
        for category_id in range(num_categories):
            category_name = categories[category_id]
            writer.writerow([category_id, category_name])
        print(f'{num_categories} generated')
    return    

# populate orderItem.csv
def gen_order_item(num_order_summaries):
    print('OrderItem...', end=' ', flush=True)
    data = []
    product_listing = pd.read_csv('ProductListing.csv')
    for order_id in range(num_order_summaries):
        # ensure each order_id maps to 1-10 items
        for i in range(random.randint(1, 10)):
            # dependency on product_listing for quantity, quantity_price, and combinations of product_id and seller_id
            row = random.randrange(product_listing.shape[0])
            listing = product_listing.iloc[row]
            product_id = int(listing.iloc[0])
            seller_id = int(listing.iloc[1])
            # Order quantity is randomly <= whichever is smaller between 8 and the item's inventory_count
            max_quantity = min(int(listing.iloc[3]), 8)
            # bias quantities towards lower nums
            quantity = int(1 + (max_quantity - 1) * pow(random.random(), 2))
            quantity_price = round(float(listing.iloc[2]) * quantity, 2)
            is_fulfilled = fake.pybool()
            data.append([order_id, product_id, seller_id, quantity, quantity_price, is_fulfilled])
    # Make primary keysets unique
    df = pd.DataFrame(data, columns=['order_id', 'product_id', 'seller_id', 'quantity', 'quantity_price', 'is_fulfilled'])
    og_shape = df.shape[0]
    df = df.drop_duplicates(subset=['order_id', 'product_id', 'seller_id'])
    df.to_csv('OrderItem.csv', index=False, header=False)
    print(f'{df.shape[0]} of {og_shape} uniquely generated')
    return  

# populate orderSummary.csv
def gen_order_summary(num_order_summaries):
    print('OrderSummary...', end=' ', flush=True)
    data = []
    order_item = pd.read_csv('OrderItem.csv', names=['order_id', 'product_id', 'seller_id', 'quantity', 'quantity_price', 'is_fulfilled'])
    for order_id in range(num_order_summaries):
        user_id = random.randrange(num_accounts)
        # indirect dependency on product_listing, direct dependency on order_item for item_quantity and total_cost
        relevant_rows = order_item[order_item['order_id'] == order_id]
        total_cost = round(relevant_rows['quantity_price'].sum(), 2)
        item_quantity = relevant_rows['quantity'].sum()
        datetime_placed = fake.date_time_this_year()
        data.append([order_id, user_id, total_cost, item_quantity, datetime_placed])
    # Make primary keysets unique
    df = pd.DataFrame(data, columns=['order_id', 'user_id', 'total_cost', 'item_quantity', 'datetime_placed'])
    df = df.drop_duplicates(subset=['order_id'])
    df.to_csv('OrderSummary.csv', index=False, header=False)
    print(f'{df.shape[0]} of {num_order_summaries} uniquely generated')
    return  

# populate product.scv
# product has continuous product_id in num_products
def gen_product(num_products):
    with open('Product.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Product...', end=' ', flush=True)
        for product_id in range(num_products):
            product = parsed_beauty[product_id]
            category_id = random.randrange(num_categories)
            product_name = product["title"][0:254]
            product_description = " ".join(product["description"])[0:3999]
            image_url = product["images"][0]["hi_res"]
            writer.writerow([product_id, category_id, product_name, product_description, image_url])
        print(f'{num_products} generated')
    return 

# populate productListing.csv
def gen_product_listing(num_product_listings):
    print('ProductListing...', end=' ', flush=True)
    data = []
    for uid in range(num_product_listings):
        product_id = random.randrange(num_products)
        seller_id = random.randrange(num_accounts//3)*3
        # get prices from JSON and let sellers randomly set prices as ±30% of the default price
        default_price = parsed_beauty[product_id]["price"]
        amount_changed = random.randrange(0, max(1, int(default_price*0.3)))
        sign = random.choice([1,-1])
        price = round(default_price + (amount_changed*sign), 2)
        inventory_count = random.randrange(1,250)
        data.append([product_id, seller_id, price, inventory_count])
    # Make primary keysets unique
    df = pd.DataFrame(data, columns=['product_id', 'seller_id', 'price', 'inventory_count'])
    df = df.drop_duplicates(subset=['product_id', 'seller_id'])
    df.to_csv('ProductListing.csv', index=False, header=False)
    print(f'{df.shape[0]} of {num_product_listings} uniquely generated')
    return  

# populate productReviews.csv
def gen_product_reviews(num_product_reviews):
    print('ProductReviews...', end=' ', flush=True)
    data = []
    for uid in range(num_product_reviews):
        user_id = random.randrange(num_accounts)
        product_id = random.randrange(num_products)
        # make rating an int from 0-9 since rating in dataset is 0-5.0
        rating = int(beauty_reviews[uid]["rating"]*2)-1
        datetime = fake.date_time_this_year()
        # set character limits based on conditions in create.sql
        title = beauty_reviews[uid]["title"][0:255]
        description = beauty_reviews[uid]["text"][0:2500]
        if random.randint(0, 1):
            edited_on = datetime + fake.time_delta()
        else: 
            edited_on = None
        upvote_count = random.randrange(200)
        data.append([user_id, product_id, rating, datetime, title, description, upvote_count, edited_on])
    # Make primary keysets unique
    df = pd.DataFrame(data, columns=['user_id', 'product_id', 'rating', 'datetime', 'title', 'description', 'upvote_count', 'edited_on'])
    df = df.drop_duplicates(subset=['user_id', 'product_id'])
    df.to_csv('ProductReviews.csv', index=False, header=False)
    print(f'{df.shape[0]} of {num_product_reviews} uniquely generated')
    return  

# populate sellerReviews.csv
def gen_seller_reviews(num_seller_reviews):
    print('SellerReviews...', end=' ', flush=True)
    data = []
    for uid in range(num_seller_reviews):
        user_id = random.randrange(num_accounts)
        seller_id = random.randrange(num_accounts//3)*3
        # make rating an int from 0-9 since rating in dataset is 0-5.0
        rating = int(beauty_reviews[uid]["rating"]*2)-1
        datetime = fake.date_time_this_year()
        # set character limits based on conditions in create.sql
        title = beauty_reviews[uid]["title"][0:255]
        description = beauty_reviews[uid]["text"][0:2500]
        if random.randint(0, 1):
            edited_on = datetime + fake.time_delta()
        else: 
            edited_on = None
        upvote_count = random.randrange(200)
        data.append([user_id, seller_id, rating, datetime, title, description, upvote_count, edited_on])
    # Make primary keysets unique
    df = pd.DataFrame(data, columns=['user_id', 'seller_id', 'rating', 'datetime', 'title', 'description', 'upvote_count', 'edited_on'])
    df = df.drop_duplicates(subset=['user_id', 'seller_id'])
    df.to_csv('SellerReviews.csv', index=False, header=False)
    print(f'{df.shape[0]} of {num_seller_reviews} uniquely generated')
    return  

# # Populate CSV files
# # Run in order to propagate changes between dependent files
# gen_account(num_accounts)
# gen_category(num_categories)
# gen_product(num_products)
# gen_product_listing(num_products*4)
# gen_cart_item(num_accounts*5)
# # order_item and order_summary must keep the same # for their parameter
# gen_order_item(num_accounts*5)
# gen_order_summary(num_accounts*5)
# gen_product_reviews(num_products*40)
# gen_seller_reviews(num_accounts*40)

# # Test price distribution
# pl = pd.read_csv('ProductListing.csv', names=['product_id', 'seller_id', 'price', 'inventory_count'])
# print(pl['price'].describe())

# # Test table item quantities
# print("ProductListing rows with 0 inventory_count", pl[pl['inventory_count']==0].shape[0])
# ci = pd.read_csv('CartItem.csv', names=['user_id', 'product_id', 'seller_id', 'quantity', 'saved_for_later'])
# print("CartItem rows with 0 quantity", ci[ci['quantity']==0].shape[0])
# oi = pd.read_csv('OrderItem.csv', names=['order_id', 'product_id', 'seller_id', 'quantity', 'quantity_price', 'is_fulfilled'])
# print("OrderItem rows with 0 quantity", oi[oi['quantity']==0].shape[0])
# os = pd.read_csv('OrderSummary.csv', names=['order_id', 'user_id', 'total_cost', 'item_quantity', 'datetime_placed'])
# print("OrderSummary rows with 0 quantity", os[os['item_quantity']==0].shape[0])
