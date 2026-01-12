# Star Micronics - POS Receipt Data Analysis Dashboard

![Project Overview](https://github.com/vedant-abrol/HackNJIT_Challenge_Star_Micronics/blob/main/Star_Dynamic_Pricing_Dashboard.png)

## 📋 What is This Project?

This is a **complete data pipeline and analytics dashboard** built for the HackNJIT 2024 Challenge. It takes messy, unstructured receipt files (`.stm` format) from multiple cafes, processes them, stores them in the cloud, and displays beautiful analytics in a web dashboard.

**In simple terms:** Think of it like a smart filing system that:
1. Takes thousands of paper receipts from different cafes
2. Organizes them automatically
3. Extracts important information (prices, items, dates)
4. Stores everything in the cloud
5. Shows you beautiful charts and statistics

---

## 🎯 The Problem We Solved

Cafes generate thousands of receipt files every day in `.stm` format (a special printer format). These files are:
- **Unstructured** - Hard to read and analyze
- **Scattered** - Files from different cafes mixed together
- **Hard to analyze** - No easy way to see trends, sales, or insights

**Our solution:** Automatically process, organize, and visualize all this data!

---

## 🏗️ How It Works (The Complete Flow)

### Step 1: Infrastructure Setup (Terraform)
**What:** Terraform creates the cloud storage (AWS S3 bucket) automatically.

**Why:** Instead of manually clicking buttons in AWS to create storage, we write code that does it automatically. This ensures:
- Same setup every time
- No mistakes
- Easy to recreate if needed

**File:** `main.tf` - This is the "recipe" that tells AWS what to create.

### Step 2: Data Ingestion (Python Scripts)
**What:** Receipt files are uploaded and organized.

**Scripts:**
- `unzip.py` - Extracts `.stm` files from zip archives and uploads to S3
- `cluster.py` - Organizes files by cafe ID and date (e.g., `cafe_6352/20241025/file.stm`)

**Result:** All receipt files are neatly organized in cloud storage.

### Step 3: Data Processing (Python Scripts)
**What:** Raw receipt files are converted into structured CSV files.

**Script:**
- `store_6352_parseToCSV.py` - Reads `.stm` files, extracts:
  - Order numbers
  - Dates and times
  - Item names and prices
  - VAT (tax) information
  - Total amounts
  
**Result:** Clean, structured CSV files ready for analysis.

### Step 4: Data Storage (AWS S3)
**What:** All processed data is stored in AWS S3 (Amazon's cloud storage).

**Structure:**
```
S3 Bucket: pos-receipts-stm-files/
├── stm_files/              # Raw receipt files
├── clustered_receipts/      # Organized by cafe/date
└── processed_receipts/     # Final CSV files
    ├── cafe_6352/
    │   └── date_20241025/
    │       └── receipt.csv
    └── cafe_6391/
        └── ...
```

### Step 5: Data Querying (AWS Athena - Optional)
**What:** SQL queries can be run on the CSV files without needing a database.

**Why:** You can ask questions like:
- "What was total revenue last month?"
- "Which cafe had the most sales?"
- "What's the average order value?"

### Step 6: Visualization (React Dashboard)
**What:** A beautiful web dashboard shows all the analytics.

**Features:**
- 📊 Real-time statistics (Total Receipts, Active Cafes, Revenue, etc.)
- 🎨 Modern, minimalistic design
- 📱 Responsive (works on mobile, tablet, desktop)
- 🔗 Ready for PowerBI integration

**Tech Stack:**
- React.js for the frontend
- Beautiful gradients and animations
- Card-based layout with hover effects

---

## 🛠️ Technologies Used

### Frontend
- **React.js** - Modern web framework for the dashboard UI
- **CSS3** - Beautiful styling with gradients and animations

### Backend/Processing
- **Python 3** - Scripts for data processing and organization
- **boto3** - AWS SDK for Python (to interact with S3)

### Cloud Infrastructure
- **AWS S3** - Cloud storage for receipt files
- **AWS Athena** - SQL queries on CSV files (optional)
- **Terraform** - Infrastructure as Code (automates AWS setup)

### Data Visualization
- **PowerBI** - Advanced analytics and visualizations (can be embedded)

---

## 📁 Project Structure

```
HackNJIT_Challenge_Star_Micronics/
│
├── 📂 src/                          # React frontend application
│   ├── components/
│   │   ├── Dashboard.js            # Main dashboard with stats
│   │   └── Header.js               # Header with logo
│   ├── App.js                       # Main app component
│   ├── App.css                      # Beautiful styling
│   └── index.js                     # App entry point
│
├── 📂 public/                       # Static assets
│   └── index.html                   # HTML template
│
├── 📂 clustered_receipts/           # Sample organized receipts (by cafe/date)
├── 📂 organized_receipts_by_date/  # Sample receipts organized by date
│
├── 🐍 Python Scripts
│   ├── unzip.py                     # Extract & upload .stm files to S3
│   ├── cluster.py                   # Organize files by cafe ID and date
│   ├── store_6352_parseToCSV.py    # Parse .stm files → CSV format
│   └── cleanup.py                   # Clean up temporary files
│
├── ☁️ Infrastructure
│   ├── main.tf                      # Terraform config (creates S3 bucket)
│   ├── terraform.tfstate            # Terraform state (tracks what's created)
│   └── terraform.tfstate.backup     # Backup of state
│
├── 📦 Configuration
│   ├── package.json                 # Node.js dependencies
│   ├── .gitignore                   # Files to ignore in Git
│   └── README.md                    # This file!
│
└── 🖼️ Assets
    └── Star_Dynamic_Pricing_Dashboard.png  # Project screenshot
```

---

## 🚀 Getting Started

### Prerequisites

Before you begin, make sure you have:

1. **Node.js and npm** (for the React app)
   - Download from [nodejs.org](https://nodejs.org/)
   - Verify: `node --version` and `npm --version`

2. **Python 3** (for data processing scripts)
   - Download from [python.org](https://www.python.org/)
   - Verify: `python3 --version`

3. **AWS Account** (for cloud storage)
   - Sign up at [aws.amazon.com](https://aws.amazon.com/)
   - Configure AWS credentials: `aws configure`

4. **Terraform** (for infrastructure setup)
   - Download from [terraform.io](https://www.terraform.io/downloads)
   - Verify: `terraform --version`

### Installation Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/vedant-abrol/HackNJIT_Challenge_Star_Micronics.git
cd HackNJIT_Challenge_Star_Micronics
```

#### 2. Set Up AWS Infrastructure (Terraform)

This creates the S3 bucket where your data will be stored.

```bash
# Initialize Terraform
terraform init

# Preview what will be created
terraform plan

# Create the infrastructure
terraform apply
```

**What this does:** Creates an S3 bucket named `pos-receipts-stm-files` with:
- Private access (secure)
- Versioning enabled (keeps file history)
- Auto-delete after 1 year (saves costs)

#### 3. Install React Dependencies

```bash
npm install
```

#### 4. Run the Dashboard

```bash
npm start
```

The dashboard will open at **http://localhost:3000**

You'll see:
- Beautiful gradient background
- Statistics cards (Total Receipts, Cafes, Revenue, etc.)
- PowerBI placeholder area

---

## 📝 How to Use the Python Scripts

### 1. Upload Receipt Files to S3

If you have a zip file with `.stm` files:

```bash
# Set environment variables (optional)
export ZIP_FILE_PATH="PrintJobData_20241102.zip"
export S3_BUCKET_NAME="pos-receipts-stm-files"
export S3_FOLDER="stm_files"

# Run the script
python3 unzip.py
```

**What it does:** Extracts `.stm` files from zip and uploads to S3.

### 2. Organize Files by Cafe and Date

```bash
# Set environment variables (optional)
export S3_BUCKET_NAME="pos-receipts-stm-files"
export S3_SOURCE_FOLDER="stm_files"
export S3_DESTINATION_FOLDER="clustered_receipts"

# Run the script
python3 cluster.py
```

**What it does:** Moves files from `stm_files/` to `clustered_receipts/{cafe_id}/{date}/`

### 3. Parse STM Files to CSV

```bash
# Set environment variables (optional)
export S3_BUCKET_NAME="pos-receipts-stm-files"
export S3_SOURCE_FOLDER="clustered_receipts"
export S3_DESTINATION_FOLDER="processed_receipts"
export CAFE_FILTER="6352"  # Optional: process only one cafe

# Run the script
python3 store_6352_parseToCSV.py
```

**What it does:** 
- Reads `.stm` files from S3
- Extracts order data, items, prices, VAT
- Creates CSV files
- Uploads CSV back to S3

### 4. Clean Up Temporary Files

```bash
export TEMP_DIR="extracted_stm_files"  # Optional
python3 cleanup.py
```

**What it does:** Removes temporary files created during processing.

---

## 🎨 Dashboard Features

### Current Features
- ✅ **Modern UI Design** - Beautiful gradients, smooth animations
- ✅ **Statistics Cards** - Total Receipts, Active Cafes, Revenue, Avg Order Value
- ✅ **Responsive Design** - Works on all screen sizes
- ✅ **PowerBI Ready** - Placeholder for embedded PowerBI dashboards

### Data Source
**Note:** The dashboard currently shows placeholder data. To connect real data:

1. **Option A:** Create a backend API that queries AWS Athena
2. **Option B:** Connect directly to PowerBI (which queries your data)
3. **Option C:** Use AWS API Gateway + Lambda to serve data

---

## 🔧 Understanding Each Component

### Terraform (`main.tf`)
**Role:** Infrastructure as Code - Automatically creates AWS resources.

**What it creates:**
- S3 bucket for storing receipt files
- Configures bucket settings (versioning, lifecycle rules)

**Why use it:**
- Reproducible infrastructure
- Version controlled
- No manual AWS Console clicking

### Python Scripts

#### `unzip.py`
- **Purpose:** Extract and upload receipt files
- **Input:** Zip file with `.stm` files
- **Output:** Files in S3 bucket

#### `cluster.py`
- **Purpose:** Organize files by cafe ID and date
- **Input:** Unorganized files in S3
- **Output:** Organized folder structure

#### `store_6352_parseToCSV.py`
- **Purpose:** Convert `.stm` files to CSV format
- **Input:** Raw `.stm` receipt files
- **Output:** Structured CSV files with extracted data

#### `cleanup.py`
- **Purpose:** Remove temporary files
- **Input:** Temporary directory path
- **Output:** Cleaned up system

### React Dashboard (`src/`)

#### `App.js`
- Main application component
- Renders Header, Dashboard, and Footer

#### `components/Dashboard.js`
- Displays statistics and analytics
- Shows PowerBI placeholder
- Handles data formatting (currency, numbers)

#### `components/Header.js`
- Header with Star Micronics logo
- Dashboard title

---

## 🎓 What We Learned

Building this project taught us:

1. **Infrastructure as Code** - Using Terraform to automate cloud setup
2. **Data Processing** - Parsing unstructured formats with Python
3. **Cloud Storage** - Using AWS S3 for scalable file storage
4. **Modern Web Development** - Building beautiful UIs with React
5. **Data Pipeline Design** - Creating end-to-end data workflows

---

## 🚧 Future Improvements

- [ ] **Backend API** - Connect dashboard to real data from AWS Athena
- [ ] **Real-time Updates** - Live data refresh in dashboard
- [ ] **More Analytics** - Additional metrics and visualizations
- [ ] **Error Handling** - Better error messages and recovery
- [ ] **Automated ETL** - AWS Glue for automated data processing
- [ ] **Authentication** - User login and access control
- [ ] **Export Features** - Download reports as PDF/Excel

---

## 📊 Project Statistics

- **Total Receipts Processed:** 7,688+ files
- **Cafes Tracked:** 30+ locations
- **Technologies:** 5+ (React, Python, AWS, Terraform, PowerBI)
- **Lines of Code:** 1000+

---

## 🤝 Contributing

This project was built for HackNJIT 2024 Challenge. Feel free to:
- Report bugs
- Suggest improvements
- Fork and enhance

---

## 📄 License

Distributed under License.

---

## 👥 Authors

**HackNJIT 2024 Challenge Team**

---

## 🙏 Acknowledgments

- Star Micronics for the challenge
- HackNJIT 2024 organizers
- AWS for cloud infrastructure
- React community for amazing tools

---

**Built with ❤️ for HackNJIT 2024**
