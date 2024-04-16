# 🏦 Cheque Mate 💸

Welcome to Cheque Mate, the ultimate solution for automating cheque data extraction! 🎉 This project leverages the power of OpenAI's GPT-4 to analyze cheque images and extract key information to a CSV file, making cheque processing a breeze. 😎

## 🚀 Getting Started

To get started with Cheque Mate, follow these simple steps:

1. Clone the repository:
   ```
   git clone https://github.com/kaneda2004/cheque-mate.git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a folder called `scans/` and place your cheque scans in the folder. (one per page for now)

4. Set your OpenAI API key as an environment variable:
   ```
   export OPENAI_API_KEY=your-api-key
   ```

5. Run the script:
   ```
   python main.py
   ```

Sit back and relax as Cheque Mate works its magic! 🪄✨ The extracted cheque data will be saved in the `cheque_data.csv` file.

## 📁 Project Structure

- `main.py`: The main script that orchestrates the cheque data extraction process.
- `requirements.txt`: The list of required Python dependencies.
- `scans/`: The directory where you should place your cheque scans.
- `cheque_data.csv`: The CSV file containing the extracted cheque data.

## 🌟 Use Cases

Cheque Mate has a wide range of use cases, including:

- 🏦 Banking and Financial Institutions: Automate cheque processing and data entry.
- 🧾 Accounting and Bookkeeping: Streamline cheque reconciliation and record-keeping.
- 🔍 Fraud Detection: Analyze cheque data for potential fraudulent activities.
- 📊 Data Analysis: Gain insights from cheque data for business intelligence and decision-making.

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## 🙏 Acknowledgements

We would like to express our gratitude to the OpenAI team for their incredible GPT-4 model, which powers the core functionality of Cheque Mate. 🌈

Happy cheque processing! 😄
