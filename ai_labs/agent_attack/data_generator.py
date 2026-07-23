import random
from faker import Faker
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Customer, Order, SupportTicket, create_tables, get_db, SessionLocal

fake = Faker()

class CRMDataGenerator:
    def __init__(self):
        self.membership_tiers = ["basic", "premium", "vip"]
        self.order_statuses = ["pending", "shipped", "delivered", "cancelled"]
        self.ticket_statuses = ["open", "in_progress", "resolved", "closed"]
        self.priorities = ["low", "medium", "high", "urgent"]
        self.products = [
            "Laptop Pro 15", "Wireless Headphones", "Smartphone X", "Tablet Ultra",
            "Smart Watch", "Gaming Console", "Bluetooth Speaker", "Wireless Mouse",
            "Keyboard Mechanical", "Monitor 4K", "Webcam HD", "External SSD"
        ]

    def generate_customers(self, count: int = 100):
        customers = []
        for _ in range(count):
            customer = Customer(
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone=fake.phone_number(),
                address=fake.street_address(),
                city=fake.city(),
                state=fake.state_abbr(),
                zip_code=fake.zipcode(),
                account_balance=round(random.uniform(-500, 5000), 2),
                membership_tier=random.choice(self.membership_tiers),
                created_at=fake.date_time_between(start_date="-2y", end_date="now"),
                last_contact=fake.date_time_between(start_date="-6m", end_date="now") if random.choice([True, False]) else None,
                is_active=random.choice([True, True, True, False]),  # 75% active
                notes=fake.text(max_nb_chars=200) if random.choice([True, False]) else None
            )
            customers.append(customer)
        return customers

    def generate_orders(self, customer_ids: list, count: int = 300):
        orders = []
        for _ in range(count):
            order_date = fake.date_time_between(start_date="-1y", end_date="now")
            order = Order(
                customer_id=random.choice(customer_ids),
                order_number=f"ORD-{fake.random_number(digits=8)}",
                product_name=random.choice(self.products),
                quantity=random.randint(1, 5),
                price=round(random.uniform(50, 2000), 2),
                status=random.choice(self.order_statuses),
                order_date=order_date,
                tracking_number=f"TRK{fake.random_number(digits=12)}" if random.choice([True, False]) else None
            )
            orders.append(order)
        return orders

    def generate_support_tickets(self, customer_ids: list, count: int = 150):
        ticket_subjects = [
            "Order not received", "Product defective", "Billing inquiry",
            "Account access issue", "Return request", "Shipping delay",
            "Product installation help", "Warranty claim", "Refund request",
            "Technical support needed"
        ]

        tickets = []
        for _ in range(count):
            created_date = fake.date_time_between(start_date="-6m", end_date="now")
            status = random.choice(self.ticket_statuses)

            ticket = SupportTicket(
                customer_id=random.choice(customer_ids),
                ticket_number=f"TKT-{fake.random_number(digits=6)}",
                subject=random.choice(ticket_subjects),
                description=fake.text(max_nb_chars=500),
                status=status,
                priority=random.choice(self.priorities),
                created_at=created_date,
                updated_at=created_date + timedelta(hours=random.randint(1, 48)),
                resolved_at=created_date + timedelta(days=random.randint(1, 14)) if status == "resolved" else None
            )
            tickets.append(ticket)
        return tickets

def populate_database():
    create_tables()
    db = SessionLocal()

    try:
        # Clear existing data
        db.query(SupportTicket).delete()
        db.query(Order).delete()
        db.query(Customer).delete()
        db.commit()

        generator = CRMDataGenerator()

        # Generate customers
        customers = generator.generate_customers(100)
        db.add_all(customers)
        db.commit()

        # Get customer IDs
        customer_ids = [c.id for c in db.query(Customer).all()]

        # Generate orders
        orders = generator.generate_orders(customer_ids, 300)
        db.add_all(orders)
        db.commit()

        # Generate support tickets
        tickets = generator.generate_support_tickets(customer_ids, 150)
        db.add_all(tickets)
        db.commit()

        print(f"Generated {len(customers)} customers, {len(orders)} orders, and {len(tickets)} support tickets")

    except Exception as e:
        print(f"Error populating database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_database()