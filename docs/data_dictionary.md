# Data Dictionary / Keys

| Table | Grain and PK | Main fields | Notes |
|---|---|---|---|
| `fact_orders` | One order; `order_id` | `customer_unique_id`, `purchased_at`, `state`, `status`, `gmv_brl`, `is_delivered`, `is_late`, `review_score`, `payment_method` | Facts, aggregated payment/review data |
| `fact_items` | One order line; (`order_id`, `order_item_id`) | `product_id`, `seller_id`, `price`, `item_freight_brl`, `category`, `gmv_brl` | Delivered GMV only |
| `dim_customers` | One persistent customer; `customer_unique_id` | `recency_days`, `lifetime_delivered_orders`, `lifetime_gmv_brl`, `rfm_score`, `segment` | Historical lifetime snapshot |
| `dim_products` | One product; `product_id` | `category`, `product_category_name` | Category translation provided if available |
| `dim_date` | One day; `date` | `year`, `quarter`, `month`, `year_month` | Conformed purchase calendar |

## Data lineage / original tables

`olist_orders_dataset.csv`, `olist_customers_dataset.csv`, `olist_order_items_dataset.csv`, `olist_order_payments_dataset.csv`, `olist_order_reviews_dataset.csv`, `olist_products_dataset.csv`, and `product_category_name_translation.csv` from https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce.

## Source caveats

- Some orders have no reviews, items, or payment records. Those are left joined and not fabricated.
- First payment method is a **primary-method proxy** for orders with multiple methods; summed payment values are captured separately.
- Review scores are averaged if several review records exist for one order.
- Customer segmentation applies to observed historical transactions; not verified future churn.
