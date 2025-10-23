# Pesti-Link - Connecting Farmers with Pesticide Shops

A Flask web application that connects farmers with pesticide shops, allowing shop owners to list their products and farmers to search for pesticides and fertilizers.

## Features

### For Shop Owners
- Register and manage shop account
- Add pesticide and fertilizer products with detailed specifications
- Set pricing and inventory quantities
- Specify which crops the products are suitable for
- List active chemicals/ingredients

### For Farmers
- Register and manage farmer account
- Search for pesticides by name or crop type
- View product specifications, pricing, and availability
- Find which shops have the products they need
- Receive notifications for new products

### General Features
- Responsive design with Tailwind CSS
- User authentication and session management
- MongoDB Atlas integration for data storage
- Real-time notifications system

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. MongoDB Atlas Setup
1. Create a MongoDB Atlas account at https://www.mongodb.com/atlas
2. Create a new cluster
3. Create a database user with read/write permissions
4. Get your connection string
5. Copy `env_example.txt` to `.env` and update the MongoDB URI

### 3. Environment Configuration
Create a `.env` file in the project root with:
```
SECRET_KEY=your-secret-key-here-change-in-production
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/pesti_link?retryWrites=true&w=majority
```

#### Email Notifications (Gmail SMTP)
To send email notifications to all farmers when a new product is added, configure Gmail SMTP using an App Password.

1. Enable 2‑Step Verification on your Google account.
2. Create an App Password for "Mail" on your device at `https://myaccount.google.com/apppasswords`.
3. Add the following to your `.env` file:
```
# Gmail SMTP credentials (App Password required)
GMAIL_SMTP_USER=your_gmail_address@gmail.com
GMAIL_SMTP_APP_PASSWORD=your_16_char_app_password

# Optional: disable email notifications (default: true)
EMAIL_NOTIFICATIONS_ENABLED=true
```
The application will connect to `smtp.gmail.com:587` using TLS and send plain-text emails to all users with `user_type = "farmer"`.

### 4. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
pest-link/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── env_example.txt       # Environment variables template
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── shop_dashboard.html
│   ├── farmer_dashboard.html
│   ├── add_product.html
│   ├── search.html
│   └── notifications.html
└── static/               # Static files (CSS, JS, images)
    ├── css/
    └── js/
```

## Database Collections

### Users Collection
- `username`: User's display name
- `email`: User's email address
- `password`: Hashed password
- `user_type`: Either "farmer" or "shop_owner"
- `created_at`: Account creation timestamp

### Products Collection
- `name`: Product name
- `specifications`: Detailed product specifications
- `cost`: Price per unit
- `quantity`: Available quantity
- `crop_type`: Suitable crop type
- `chemicals`: Active chemicals/ingredients
- `shop_owner_id`: Reference to shop owner
- `shop_name`: Shop owner's username
- `created_at`: Product creation timestamp

### Notifications Collection
- `type`: Notification type (new_product, update, etc.)
- `title`: Notification title
- `message`: Notification message
- `product_id`: Reference to product (if applicable)
- `created_at`: Notification creation timestamp

## Usage

1. **Registration**: Users can register as either farmers or shop owners
2. **Shop Owners**: Can add products with detailed specifications
3. **Farmers**: Can search for products and view notifications
4. **Search**: Farmers can search by product name or crop type
5. **Notifications**: Farmers receive notifications when new products are added

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Database**: MongoDB Atlas (cloud database)
- **Frontend**: HTML, Tailwind CSS (via CDN)
- **Authentication**: Werkzeug password hashing
- **Icons**: Font Awesome

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
