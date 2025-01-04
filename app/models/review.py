from flask import current_app as app

from flask_login import current_user

class Review:
    def __init__(self, user_id, reviewed_id, name, rating, datetime, title, description, upvote_count, edited_on, review_type):
        self.user_id = user_id
        self.reviewed_id = reviewed_id
        self.name = name
        self.rating = rating                # int between 0 through 9 (representing 0.5 through 5.0 stars, in half-star increments)
        self.datetime = datetime
        self.title = title
        self.description = description
        self.upvote_count = upvote_count
        self.edited_on = edited_on          # datetime format
        self.review_type = review_type      # review_type is a string: either 'Product' or 'Seller'

    @staticmethod
    def review_get_userid(user_id, get_count, order_by='datetime'):
        if order_by == 'upvote_count':
            rows = app.db.execute('''
            SELECT PR.user_id, PR.product_id AS reviewed_id, P.product_name AS name, PR.rating, PR.datetime, PR.title, PR.description, PR.upvote_count, PR.edited_on, 'Product' AS review_type
            FROM ProductReviews PR
            JOIN Product P ON PR.product_id = P.product_ID
            WHERE PR.user_id = :user_id
        
            UNION ALL
        
            SELECT SR.user_id, SR.seller_id AS reviewed_id, A.full_name AS name, SR.rating, SR.datetime, SR.title, SR.description, SR.upvote_count, SR.edited_on, 'Seller' AS review_type
            FROM SellerReviews SR
            JOIN Account A ON SR.seller_id = A.user_id
            WHERE SR.user_id = :user_id
        
            ORDER BY upvote_count DESC
            LIMIT :get_count''',
            user_id=user_id,
            get_count=get_count)
        else:
            rows = app.db.execute('''
            SELECT PR.user_id, PR.product_id AS reviewed_id, P.product_name AS name, PR.rating, PR.datetime, PR.title, PR.description, PR.upvote_count, PR.edited_on, 'Product' AS review_type
            FROM ProductReviews PR
            JOIN Product P ON PR.product_id = P.product_ID
            WHERE PR.user_id = :user_id
        
            UNION ALL
        
            SELECT SR.user_id, SR.seller_id AS reviewed_id, A.full_name AS name, SR.rating, SR.datetime, SR.title, SR.description, SR.upvote_count, SR.edited_on, 'Seller' AS review_type
            FROM SellerReviews SR
            JOIN Account A ON SR.seller_id = A.user_id
            WHERE SR.user_id = :user_id
        
            ORDER BY datetime DESC
            LIMIT :get_count''',
            user_id=user_id,
            get_count=get_count)

        return [Review(*row) for row in rows] if rows else []
    
    @staticmethod
    def review_get_sellerid(seller_id, get_count, order_by='datetime'):
        if order_by == 'upvote_count':
            rows = app.db.execute('''
            SELECT SR.user_id, SR.seller_id AS reviewed_id, A.full_name AS name, SR.rating, SR.datetime, SR.title, SR.description, SR.upvote_count, SR.edited_on, 'Seller' AS review_type
            FROM SellerReviews SR
            JOIN Account A ON SR.seller_id = A.user_id
            WHERE SR.seller_id = :seller_id
        
            ORDER BY upvote_count DESC
            LIMIT :get_count''',
            seller_id=seller_id,
            get_count=get_count)
        else:
            rows = app.db.execute('''
            SELECT SR.user_id, SR.seller_id AS reviewed_id, A.full_name AS name, SR.rating, SR.datetime, SR.title, SR.description, SR.upvote_count, SR.edited_on, 'Seller' AS review_type
            FROM SellerReviews SR
            JOIN Account A ON SR.seller_id = A.user_id
            WHERE SR.seller_id = :seller_id
        
            ORDER BY datetime DESC
            LIMIT :get_count''',
            seller_id=seller_id,
            get_count=get_count)

        return [Review(*row) for row in rows] if rows else []
    
    @staticmethod
    def review_get_productid(product_id, get_count, order_by='datetime'):
        if order_by == 'upvote_count':
            rows = app.db.execute('''
            SELECT PR.user_id, PR.product_id AS reviewed_id, P.product_name AS name, PR.rating, PR.datetime, PR.title, PR.description, PR.upvote_count, PR.edited_on, 'Product' AS review_type
            FROM ProductReviews PR
            JOIN Product P ON PR.product_id = P.product_id
            WHERE PR.product_id = :product_id
        
            ORDER BY upvote_count DESC
            LIMIT :get_count''',
            product_id=product_id,
            get_count=get_count)
        else:
            rows = app.db.execute('''
            SELECT PR.user_id, PR.product_id AS reviewed_id, P.product_name AS name, PR.rating, PR.datetime, PR.title, PR.description, PR.upvote_count, PR.edited_on, 'Product' AS review_type
            FROM ProductReviews PR
            JOIN Product P ON PR.product_id = P.product_id
            WHERE PR.product_id = :product_id
        
            ORDER BY datetime DESC
            LIMIT :get_count''',
            product_id=product_id,
            get_count=get_count)

        return [Review(*row) for row in rows] if rows else []
    
    @staticmethod
    def create_product_review(user_id, product_id, rating, title, description):
        app.db.execute('''
            INSERT INTO ProductReviews (user_id, product_id, rating, title, description, upvote_count)
            VALUES (:user_id, :product_id, :rating, :title, :description, 0)
        ''',
        user_id=user_id,
        product_id=product_id,
        rating=rating,
        title=title,
        description=description)
        return
    
    @staticmethod
    def create_seller_review(user_id, seller_id, rating, title, description):
        app.db.execute('''
            INSERT INTO SellerReviews (user_id, seller_id, rating, title, description, upvote_count)
            VALUES (:user_id, :seller_id, :rating, :title, :description, 0)
        ''',
        user_id=user_id,
        seller_id=seller_id,
        rating=rating,
        title=title,
        description=description)
        return
    
    @staticmethod
    def delete_product_review(user_id, product_id):
        app.db.execute('''
            DELETE FROM ProductReviews
                WHERE ProductReviews.user_id = :user_id
                    AND ProductReviews.product_id = :product_id
        ''',
        user_id=user_id,
        product_id=product_id)

        # Also delete all existing upvotes from upvote table
        app.db.execute('''
            DELETE FROM ProductReviewUpvote
                WHERE ProductReviewUpvote.reviewer_id = :user_id
                    AND ProductReviewUpvote.product_id = :product_id
        ''',
        user_id=user_id,
        product_id=product_id)

        return
    
    @staticmethod
    def delete_seller_review(user_id, seller_id):
        app.db.execute('''
            DELETE FROM SellerReviews
                WHERE SellerReviews.user_id = :user_id
                    AND SellerReviews.seller_id = :seller_id
        ''',
        user_id=user_id,
        seller_id=seller_id)

        # Also delete all existing upvotes from upvote table
        app.db.execute('''
            DELETE FROM SellerReviewUpvote
                WHERE SellerReviewUpvote.reviewer_id = :user_id
                    AND SellerReviewUpvote.seller_id = :seller_id
        ''',
        user_id=user_id,
        seller_id=seller_id)

        return
    
    @staticmethod
    def update_product_review(user_id, product_id, new_rating, new_title, new_description):
        app.db.execute('''
            UPDATE ProductReviews
            SET rating = :new_rating, title = :new_title, description = :new_description, edited_on = CURRENT_TIMESTAMP
            WHERE user_id = :user_id AND product_id = :product_id
        ''',
        user_id=user_id,
        product_id=product_id,
        new_rating=new_rating,
        new_title=new_title,
        new_description=new_description)
        return
    
    @staticmethod
    def update_seller_review(user_id, seller_id, new_rating, new_title, new_description):
        app.db.execute('''
            UPDATE SellerReviews
            SET rating = :new_rating, title = :new_title, description = :new_description, edited_on = CURRENT_TIMESTAMP
            WHERE user_id = :user_id AND seller_id = :seller_id
        ''',
        user_id=user_id,
        seller_id=seller_id,
        new_rating=new_rating,
        new_title=new_title,
        new_description=new_description)
        return
    
    @staticmethod
    def upvote_product_review(reviewer_id, product_id, upvoter_id, downvote=False):
        if downvote is False:
            app.db.execute('''
                UPDATE ProductReviews
                    SET upvote_count = upvote_count + 1
                    WHERE user_id = :reviewer_id_value
                        AND product_id = :product_id_value;
            ''',
            reviewer_id_value=reviewer_id,
            product_id_value=product_id)

            app.db.execute(
                '''
                INSERT INTO ProductReviewUpvote(reviewer_id, product_id, upvoter_id)
                VALUES (:reviewer_id, :product_id, :upvoter_id);
                ''',
                reviewer_id=reviewer_id,
                product_id=product_id,
                upvoter_id=upvoter_id
            )
        else:
            app.db.execute('''
                UPDATE ProductReviews
                    SET upvote_count = upvote_count - 1
                    WHERE user_id = :reviewer_id_value
                        AND product_id = :product_id_value
                        AND upvote_count > 0;
            ''',
            reviewer_id_value=reviewer_id,
            product_id_value=product_id)
        return
    
    @staticmethod
    def upvote_seller_review(reviewer_id, seller_id, upvoter_id, downvote=False):
        if downvote is False:
            app.db.execute('''
                UPDATE SellerReviews
                    SET upvote_count = upvote_count + 1
                    WHERE user_id = :reviewer_id_value
                        AND seller_id = :seller_id_value;
            ''',
            reviewer_id_value=reviewer_id,
            seller_id_value=seller_id)

            app.db.execute(
                '''
                INSERT INTO SellerReviewUpvote(reviewer_id, seller_id, upvoter_id)
                VALUES (:reviewer_id, :seller_id, :upvoter_id);
                ''',
                reviewer_id=reviewer_id,
                seller_id=seller_id,
                upvoter_id=upvoter_id
            )
        else:
            app.db.execute('''
                UPDATE SellerReviews
                    SET upvote_count = upvote_count - 1
                    WHERE user_id = :reviewer_id_value
                        AND seller_id = :seller_id_value
                        AND upvote_count > 0;
            ''',
            reviewer_id_value=reviewer_id,
            seller_id_value=seller_id)
        return
    
    @staticmethod
    def remove_upvote_product_review(reviewer_id, product_id, upvoter_id, remove_downvote=False):
        if remove_downvote is False:
            app.db.execute('''
                UPDATE ProductReviews
                    SET upvote_count = upvote_count - 1
                    WHERE user_id = :reviewer_id_value
                        AND product_id = :product_id_value;
            ''',
            reviewer_id_value=reviewer_id,
            product_id_value=product_id)
            
            app.db.execute('''
                DELETE FROM ProductReviewUpvote P
                    WHERE P.upvoter_id = :upvoter_id
                        AND P.reviewer_id = :reviewer_id
                        AND P.product_id = :product_id;
            ''',
            upvoter_id=upvoter_id,
            reviewer_id=reviewer_id,
            product_id=product_id)
        else:
            app.db.execute('''
                UPDATE ProductReviews
                    SET upvote_count = upvote_count + 1
                    WHERE user_id = :reviewer_id_value
                        AND product_id = :product_id_value
                        AND upvote_count > 0;
            ''',
            reviewer_id_value=reviewer_id,
            product_id_value=product_id)
        return
    
    @staticmethod
    def remove_upvote_seller_review(reviewer_id, seller_id, upvoter_id, remove_downvote=False):
        if remove_downvote is False:
            app.db.execute('''
                UPDATE SellerReviews
                    SET upvote_count = upvote_count - 1
                    WHERE user_id = :reviewer_id_value
                        AND seller_id = :seller_id_value;
            ''',
            reviewer_id_value=reviewer_id,
            seller_id_value=seller_id)
            
            app.db.execute('''
                DELETE FROM SellerReviewUpvote S
                    WHERE S.upvoter_id = :upvoter_id
                        AND S.reviewer_id = :reviewer_id
                        AND S.seller_id = :seller_id;
            ''',
            upvoter_id=upvoter_id,
            reviewer_id=reviewer_id,
            seller_id=seller_id)
        else:
            app.db.execute('''
                UPDATE SellerReviews
                    SET upvote_count = upvote_count + 1
                    WHERE user_id = :reviewer_id_value
                        AND seller_id = :seller_id_value
                        AND upvote_count > 0;
            ''',
            reviewer_id_value=reviewer_id,
            seller_id_value=seller_id)
        return

    @staticmethod
    def check_if_upvoted(upvoter_id, reviewer_id, reviewed_id, review_type):
        if review_type == "Product":
            result = app.db.execute(
                '''
                SELECT P.upvoter_id
                FROM ProductReviewUpvote P
                WHERE P.upvoter_id = :upvoter_id
                    AND P.reviewer_id = :reviewer_id
                    AND P.product_id = :reviewed_id;
                ''',
                upvoter_id=upvoter_id,
                reviewer_id=reviewer_id,
                reviewed_id=reviewed_id
            )
        else:
            result = app.db.execute(
                '''
                SELECT S.upvoter_id
                FROM SellerReviewUpvote S
                WHERE S.upvoter_id = :upvoter_id
                    AND S.reviewer_id = :reviewer_id
                    AND S.seller_id = :reviewed_id;
                ''',
                upvoter_id=upvoter_id,
                reviewer_id=reviewer_id,
                reviewed_id=reviewed_id
            )
        return bool(result)
    
    @staticmethod
    def check_then_add_upvote(upvoter_id, reviewer_id, reviewed_id, review_type):
        if Review.check_if_upvoted(upvoter_id, reviewer_id, reviewed_id, review_type) is True:
            return
        if review_type == "Product":
            Review.upvote_product_review(reviewer_id, reviewed_id, upvoter_id)
        else:
            Review.upvote_seller_review(reviewer_id, reviewed_id, upvoter_id)

    @staticmethod
    def check_then_remove_upvote(upvoter_id, reviewer_id, reviewed_id, review_type):
        if Review.check_if_upvoted(upvoter_id, reviewer_id, reviewed_id, review_type) is False:
            return
        if review_type == "Product":
            Review.remove_upvote_product_review(reviewer_id, reviewed_id, upvoter_id)
        else:
            Review.remove_upvote_seller_review(reviewer_id, reviewed_id, upvoter_id)

    @staticmethod
    def get_average_rating_for_seller(seller_id):
        rows = app.db.execute('''
            SELECT COUNT(*) AS review_count, SUM(rating) AS total_rating
            FROM SellerReviews
            WHERE seller_id = :seller_id
        ''', seller_id=seller_id)

        if rows and rows[0][0] > 0:  # Accessing count as rows[0][0] and total rating as rows[0][1]
            review_count = rows[0][0]
            total_rating = rows[0][1]
            average_rating = total_rating*1.0 / review_count
            return average_rating, review_count
        else:
            return 0, 0  # No reviews available
        
    @staticmethod
    def get_average_rating_for_product(product_id):
        rows = app.db.execute('''
            SELECT COUNT(*) AS review_count, SUM(rating) AS total_rating
            FROM ProductReviews
            WHERE product_id = :product_id
        ''', product_id=product_id)

        if rows and rows[0][0] > 0:  # Accessing count as rows[0][0] and total rating as rows[0][1]
            review_count = rows[0][0]
            total_rating = rows[0][1]
            average_rating = total_rating*1.0 / review_count
            return average_rating, review_count
        else:
            return 0, 0  # No reviews available
        
    @staticmethod
    def product_review_exists(user_id, product_id):
        rows = app.db.execute(
            '''
            SELECT COUNT(*) FROM ProductReviews WHERE user_id = :user_id AND product_id = :product_id
            ''', user_id=user_id, product_id=product_id
        )
        if rows and rows[0][0] > 0:
            return True # return True if user has an existing review for the seller
        return False
        
    @staticmethod
    def can_leave_new_product_review(user_id, product_id):
        if Review.product_review_exists(user_id, product_id):
            return False
        
        has_purchased = app.db.execute('''
            SELECT COUNT(*)
            FROM OrderItem OI
            JOIN OrderSummary OS ON OI.order_id = OS.order_id
            WHERE OS.user_id = :user_id AND OI.product_id = :product_id
        ''', user_id=user_id, product_id=product_id)
        
        if has_purchased[0][0] > 0:
            return True

        return False
        
    @staticmethod
    def seller_review_exists(user_id, seller_id):
        rows = app.db.execute(
            '''
            SELECT COUNT(*) FROM SellerReviews WHERE user_id = :user_id AND seller_id = :seller_id
            ''', user_id=user_id, seller_id=seller_id
        )
        if rows and rows[0][0] > 0:
            return True # return True if user has an existing review for the seller
        return False
        
    @staticmethod
    def can_leave_new_seller_review(user_id, seller_id):
        if Review.seller_review_exists(user_id, seller_id):
            return False

        if user_id == str(seller_id):
            return False
        
        has_purchased = app.db.execute('''
            SELECT COUNT(*)
            FROM OrderItem OI
            JOIN OrderSummary OS ON OI.order_id = OS.order_id
            WHERE OS.user_id = :user_id AND OI.seller_id = :seller_id
        ''', user_id=user_id, seller_id=seller_id)
        
        if has_purchased[0][0] > 0:
            return True

        return False

    @staticmethod
    def get_product_review(user_id, product_id):
        rows = app.db.execute('''
            SELECT user_id, product_id, rating, title, description
            FROM ProductReviews
            WHERE user_id = :user_id AND product_id = :product_id
        ''',
        user_id=user_id,
        product_id=product_id)
        
        return rows[0] if rows else None

    @staticmethod
    def get_seller_review(user_id, seller_id):
        rows = app.db.execute('''
            SELECT user_id, seller_id, rating, title, description
            FROM SellerReviews
            WHERE user_id = :user_id AND seller_id = :seller_id
        ''',
        user_id=user_id,
        seller_id=seller_id)
        
        return rows[0] if rows else None
