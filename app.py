# app.py

import streamlit as st
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Function to send email alert
def send_email_alert(item_name):
    # Your email configuration
    sender_email = "your_email@gmail.com"
    receiver_email = "admin_email@gmail.com"
    password = "your_email_password"

    subject = f"Low Stock Alert: {item_name}"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    body = f"{item_name} is low in stock. Please replenish the stock."
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)

# Function to add new item
def add_new_item(name, price, stock_quantity):
    conn = sqlite3.connect('ordering_system.db')
    c = conn.cursor()
    c.execute("INSERT INTO items (name, price, stock_quantity) VALUES (?, ?, ?)", (name, price, stock_quantity))
    conn.commit()
    conn.close()

# Function to get items
def get_items():
    conn = sqlite3.connect('ordering_system.db')
    c = conn.cursor()
    c.execute("SELECT id, name, price, stock_quantity FROM items")
    items = c.fetchall()
    conn.close()
    return items

# Function to get stock quantity for a specific item
def get_stock_quantity(item_name):
    conn = sqlite3.connect('ordering_system.db')
    c = conn.cursor()
    c.execute("SELECT stock_quantity FROM items WHERE name = ?", (item_name,))
    stock_quantity = c.fetchone()[0]
    conn.close()
    return stock_quantity

# Function to submit order
def submit_order(order_items):
    conn = sqlite3.connect('ordering_system.db')
    c = conn.cursor()

    # Create a new table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS order_details (
            order_id TEXT,
            item_name TEXT,
            quantity INTEGER,
            price REAL
        )
    ''')

    # Generate a unique order ID based on the current timestamp
    order_id = datetime.now().strftime('%Y%m%d%H%M%S%f')

    # Insert order details into the table
    for item in order_items:
        c.execute("INSERT INTO order_details (order_id, item_name, quantity, price) VALUES (?, ?, ?, ?)",
                  (order_id, item['item_name'], item['quantity'], item['price']))

        # Update stock_quantity in items table
        c.execute("UPDATE items SET stock_quantity = stock_quantity - ? WHERE name = ?",
                  (item['quantity'], item['item_name']))

    conn.commit()
    conn.close()

# Streamlit app
def main():
    st.title("Ordering System")

    # Order page
    st.subheader("Order Page")

    # Check if 'order_items' exists in session_state
    if 'order_items' not in st.session_state:
        st.session_state.order_items = []

    item_name = st.selectbox("Select Item", [item[1] for item in get_items()])
    quantity = st.number_input("Enter Quantity", min_value=1, value=1)

    selected_item = [item for item in get_items() if item[1] == item_name]
    if selected_item:
        selected_item = selected_item[0]
        price = selected_item[2]
        total_amount = price * quantity
        st.write(f"Price: ${price:.2f}")
        st.write(f"Total Amount: ${total_amount:.2f}")

        if st.button("Add to Order"):
            if quantity > selected_item[3]:
                st.error("Order quantity exceeds available stock. Please reduce the quantity.")
            elif quantity > selected_item[3]:
                st.error("Order quantity exceeds available stock. Please reduce the quantity.")
            elif quantity > selected_item[3]:
                st.error("Order quantity exceeds available stock. Please reduce the quantity.")
            else:
                st.session_state.order_items.append({
                    'item_name': selected_item[1],
                    'quantity': quantity,
                    'price': selected_item[2]
                })
                st.success("Item added to order!")

    # Order summary
    st.subheader("Order Summary")

    total_order_amount = sum(item['quantity'] * item['price'] for item in st.session_state.order_items)

    for item in st.session_state.order_items:
        st.write(f"{item['item_name']} - Quantity: {item['quantity']}, Price: ${item['price']:.2f}")

        # Check if the order quantity exceeds the available stock
        if item['quantity'] > get_stock_quantity(item['item_name']):
            st.warning(f"Warning: Order quantity for {item['item_name']} exceeds available stock.")

    st.write(f"Total Order Amount: ${total_order_amount:.2f}")

    # Submit order
    if st.button("Submit Order"):
        submit_order(st.session_state.order_items)
        # Add code to send email alerts for low stock items or perform other actions as needed
        st.success("Order submitted!")

    # New Order button
    if st.button("New Order"):
        st.session_state.order_items = []  # Clear the order_items session variable
        st.success("New order started!")
        st.experimental_rerun()

    # New Item page in sidebar
    st.sidebar.title("New Item Page")

    new_item_name = st.sidebar.text_input("New Item Name")
    new_item_price = st.sidebar.number_input("New Item Price", min_value=0.01, value=1.00)
    new_item_stock = st.sidebar.number_input("New Item Stock Quantity", min_value=0, value=10)

    if st.sidebar.button("Add New Item"):
        add_new_item(new_item_name, new_item_price, new_item_stock)
        st.sidebar.success("New item added!")

if __name__ == '__main__':
    main()