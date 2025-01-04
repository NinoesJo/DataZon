Team Name: DataDawgs

We chose the standard project option. 
GitLab Repo: https://gitlab.oit.duke.edu/gkm14/mini-amazon-skeleton-24-fall/-/tree/main

- table creation/load files are located in /db
- generated .csv data are in /db/generated
- controllers are in /app
- .html frontend files are in /app/templates
- SQL/python models are in /app/models

================================================================

Team Members & Roles: 
- Sellers (Inventory & Order Fulfillment): Ashley Wilson
- Social (Feedback & Messaging): Calvin Chen
- Products: Kendi Miriti
- Users (Accounts & Purchases): Raydon Muregi
- Carts (Carts & Orders): Johan Nino Espino

================================================================

Summary of progress up to MILESTONE 2:

- Sellers (Ashley)
    Read through all project files, installed current skeleton, and developed a plan for database and website design relating to all Sellers features. 
    Merged user flow charts created for individual sections into one coherent diagram that maps out all website pages and functionalities.
- Social (Calvin)
    Cloned project and installed skeleton. Created and recorded relational schema and overall user flow plan for Product and Seller reviews on the main PDF.
- Products (Kendi)
    Cloned the project files, read through the tutorial and skeleton code. Installed and ran the skeleton. Created a user flow chart and database design for the Products functionality.
- Users (Raydon)
    Read through the details of the standard project. installed the skeleton. Created a user flow chart for Accounts & Purchases. 
- Carts (Johan)
    Cloned the project files and installed the skeleton. Read the details of the of the standard project. Created a user flow chart and the schema for the Carts functionality.

================================================================

Summary of progress up to MILESTONE 3:

MS3 Demo Video: https://drive.google.com/file/d/11hGppzEhvCwFEytB1uziwNu_AWdshFE_/view?usp=sharing

-Frontend (Raydon & Johan)
-Developed the frontend components in HTML to facilitate user interaction with the backend APIs.
-Collaborated in the successful integration and consumption of the five key API endpoints.
-Streamlined project structure and resolved merge conflicts to ensure a cohesive codebase.

-Database (Johan, Calvin, Ashley, Kendi)
-Unified and normalized all schema outlined in Milestone 2. 
-Wrote SQL queries and create table statements for the newly defined schemata.
-Created the CSV files to test queries and display data onto frontend.
-Updated the create.sql and load.sql based on our schema.

-Backend (Johan, Calvin, Kendi)
-Develpoed the models that were necessay to run the required 5 queries.
-Created the routing to connect the API endpoints to frontend.
-Updated the blueprint on __init__.py to run the controllers.

================================================================

Summary of progress up to MILESTONE 4:

Code for creating/populating a larger database: https://gitlab.oit.duke.edu/gkm14/mini-amazon-skeleton-24-fall/-/tree/main/db/generated?ref_type=heads
Reference gen_csv.py in the linked folder.

MS4 Demo Video: https://drive.google.com/file/d/1MpTzeCNHUBGxL6toV0O-00cb3AREvKRk/view?usp=drive_link

-Cart & Order (Johan)
-Developed the code where the user can change the saved for later status from the cart item.
-On the frontend, separate the Main Cart and Saved For Later Cart.
-Display the total cost of all the items that are in the Main Cart.
-Sorted the Order Summary table in descending order based on datetime.
-Created the index page and the navigation bar to quickly navigate to different web pages much more quickly.

- Database Extension & Sellers (Ashley)
- Developed functions to generate large amounts of fake data for all tables in our database.
- Tested functions to ensure unique keys and valid cross-referencing for all tables with dependencies (guarenteeing there are no foreign key lookup errors). 
- Created realistic data for Category, Account, CartItem, OrderItem, OrderSummary, and ProductListing. 
- Developing more realistic product images, descriptions, titles, and reviews. 

-Products (Kendi)
-Changed view from a singular table to each product in a tile 
-Added ‘back to products’ and ‘add to cart’ buttons
-Listing products by category
-Search and filter functionality

- Reviews/Social (Calvin Chen)
- Quick retrieval of reviews written by a user
- Updated review-details display formatting: neatly presented layout of star rating, review title, review description, date written/edited, and upvote count.
- converting 0-9 “rating” integer value to a visual star-based representation (0.5 stars through 5.0 stars)
- filter to only show top 5, 15, 50, etc. reviews
- sort results by either most recently posted or most upvoted
- UPVOTE SYSTEM:
- Two new tables to store which users have upvoted which reviews
- Live querying of upvote count, to retrieve most recent value
- Dynamic UI changes (button text, site text) to reflect whether a user has upvoted a review or not
- Rate-limiting: max of 100 upvote additions/removals per minute from a given IP.
- FUTURE IMPLEMENTATIONS:
- Add reviews list to product and user pages
- Determine who is the current user based on login, and present features accordingly:
- Will not allow a user to write multiple reviews for a single product or seller.
- Will not allow a user to write reviews on himself or a product he is selling.
- Upvote tracking. Each user can only upvote a review once.
- Enable user to write reviews and delete reviews that they have written

User(Raydon)
- Developing the user profile feature, allowing users to update personal information such as name, email, and profile picture.
FUTURE WORK
-Set up validation checks to ensure data accuracy and prevent unauthorized changes.
-Improve profile customization options for a more personalized user experience.
-Add account recovery options for forgotten passwords 

================================================================

Summary of progress up to FINAL SUBMISSION:

We all prefer team score option for grading.

Demo Video: https://drive.google.com/file/d/1f6YUJQk1CysEkcQy1OHQbrSvA8sdjb-p/view?usp=sharing

- Database Extension & Sellers (Ashley)
- Retrieved real product and review data from Amazon to populate database. Particularly for product images and prices, review ratings, and both product and review descriptions/titles. 
- Adjusted and created new parameters for fabricated data to maximize realism and ensure consistency between linked tables. 
- Increased database size by 15x.
- Updated database schema to change primary key of OrderSummary.
- Constructed front end and corresponding controller functions for logged-in sellers to update inventory quantities and create new product listings.

- Carts/Orders/Accounts/Order Fulfillment/Products (Johan Nino Espino)
- Adding the functionality of adding items to cart, updating item quantity, delete cart item, and moving items into Saved For Later.
- Completed the checkout and submit order process in which checks on the user's balance and the product inventory from the seller to successfully submit an order.
- Developed the Checkout Page which allow the user to checkout along with changing their shipping address.
- Developed the Order Summary Page which allow the user to see the order that they submitted and see if the order was able to process through.
- Added a filtering functionality on the Order Page which allow the user sort orders based on date, total cost, and total quantity.
- Created the Account Page which allow the user display their information as well as changing their address, email, name, password, and balance if what the user input the new information is valid.
- Designed the navigation bar which display the log in, register, and log out button as well as the user's name if logged in.
- Develop the functionality and frontend of Order Fulfillment Page which allow the seller to fulfilled orders as well as sort the orders based on date, earnings, quantity, and fulfillment status, as well as seeing the customer's information.
- Fixed bugs with the Product Page, added pagination below the Product Page, and develop the functionality to allow user to filter products based on category.

-Login/Products/Sellers/Reviews (Calvin Chen)
- Developed the Login and Register functionality.
- Created the functionality of allowing users review products or sellers if they already order that product or seller before.
- Designed the Seller Dashboard Page which allow the seller to view, delete, and update their product listing.
- Developed the functionality to allow sellers to add an existing product or create a new product for their product listing.
- Manage to implement images on products.
- Designed the Product Detail Page, Seller Review Page, and Account Page which shows the user's own review or customer's reviews if the user is a seller.
- Added conditionals which allow the user to see different link options based if a user a guest, buyer, or seller on the Homepage.

- Products and Report (Kendi Miriti)
- Helped design the Product Page and help categorize products to display products based on category.
- Developed the functionality of the search bar for the Product Page.
- Helped wrote and designed the Report.pdf.

- Login, Video Recording, and Frontend Style (Raydon Muregi)
- Implement the basic functionality of login.
- Added the css style for the html files.
- Helped record the final demo video.