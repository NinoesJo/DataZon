--\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
--SELECT pg_catalog.setval('public.users_id_seq',
--                         (SELECT MAX(id)+1 FROM Users),
--                         false);

--\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
--SELECT pg_catalog.setval('public.products_id_seq',
--                         (SELECT MAX(id)+1 FROM Products),
--                         false);

--\COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV
--SELECT pg_catalog.setval('public.purchases_id_seq',
--                         (SELECT MAX(id)+1 FROM Purchases),
--                         false);

\COPY Account FROM 'Account.csv' WITH DELIMITER ',' NULL '' CSV;
--SELECT pg_catalog.setval('public.user_id_seq',
--                        (SELECT MAX(user_id)+1 FROM Account),
--                        false);

\COPY Category FROM 'Category.csv' WITH DELIMITER ',' NULL '' CSV;
--SELECT pg_catalog.setval('public.category_id_seq',
--                        (SELECT MAX(category_id)+1 FROM Category),
--                        false);

\COPY Product FROM 'Product.csv' WITH DELIMITER ',' NULL '' CSV;
--SELECT pg_catalog.setval('public.product_id_seq',
--                        (SELECT MAX(product_id)+1 FROM Product),
--                        false);

\COPY ProductListing FROM 'ProductListing.csv' WITH DELIMITER ',' NULL '' CSV;

\COPY OrderSummary FROM 'OrderSummary.csv' WITH DELIMITER ',' NULL '' CSV;
--SELECT pg_catalog.setval('public.order_id_seq',
--                        (SELECT MAX(order_id)+1 FROM OrderSummary),
--                        false);

\COPY OrderItem FROM 'OrderItem.csv' WITH DELIMITER ',' NULL '' CSV;

\COPY CartItem FROM 'CartItem.csv' WITH DELIMITER ',' NULL '' CSV;

\COPY ProductReviews FROM 'ProductReviews.csv' WITH DELIMITER ',' NULL '' CSV;

\COPY SellerReviews FROM 'SellerReviews.csv' WITH DELIMITER ',' NULL '' CSV;
