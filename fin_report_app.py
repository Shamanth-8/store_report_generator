import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from datetime import datetime
import os
import tempfile

# Set page configuration
st.set_page_config(page_title="Financial Report Generator", 
                   page_icon="📊", 
                   layout="wide")

# Set style
st.markdown("""
<style>
body {
    font-family: Arial, sans-serif;
}
.report-header {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 20px;
}
.metric-card {
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 15px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# Create temporary directory for file uploads
temp_dir = tempfile.TemporaryDirectory()

def generate_data():
    """Generate realistic financial data for demonstration"""
    np.random.seed(42)
    
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    
    # Create income data
    income_data = {
        'date': dates,
        'category': np.random.choice(['Product Sales', 'Service Fees', 'Interest Income', 'Other Income'], size=len(dates)),
        'amount': np.random.randint(500, 20000, size=len(dates))
    }
    
    # Create expense data
    expense_data = {
        'date': dates,
        'category': np.random.choice(['Cost of Goods Sold', 'Rent', 'Employee Salaries', 'Utilities', 'Marketing', 'Supplies'], size=len(dates)),
        'amount': np.random.randint(300, 15000, size=len(dates))
    }
    
    # Create inventory data
    products = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    inventory_data = {
        'date': dates,
        'product': np.random.choice(products, size=len(dates)),
        'quantity': np.random.randint(50, 500, size=len(dates)),
        'cost_price': np.random.randint(10, 100, size=len(dates)),
        'selling_price': np.random.randint(50, 200, size=len(dates))
    }
    
    # Create cash flow data
    cash_flow_data = {
        'date': dates,
        'type': np.random.choice(['Inflow', 'Outflow'], size=len(dates)),
        'category': np.random.choice(['Product Sales', 'Investments', 'Loan Repayment', 'Rent', 'Employee Salaries'], size=len(dates)),
        'amount': np.random.randint(500, 20000, size=len(dates))
    }
    
    # Create more realistic data patterns
    for df in [income_data, expense_data, inventory_data, cash_flow_data]:
        if 'date' in df:
            df['date'] = pd.to_datetime(df['date'])
    
    # Convert to DataFrames
    income_df = pd.DataFrame(income_data)
    expense_df = pd.DataFrame(expense_data)
    inventory_df = pd.DataFrame(inventory_data)
    cash_flow_df = pd.DataFrame(cash_flow_data)
    
    # Add realistic business patterns
    # Simulate lower activity on weekends
    for df in [income_df, expense_df, cash_flow_df]:
        df['weekday'] = df['date'].dt.weekday
        df.loc[df['weekday'] >= 5, 'amount'] = df.loc[df['weekday'] >= 5, 'amount'] * 0.2
    
    # Simulate seasonal trends
    income_df['month'] = income_df['date'].dt.month
    income_df.loc[income_df['month'].isin([11, 12, 1]), 'amount'] *= 1.5  # Holiday season
    
    expense_df['month'] = expense_df['date'].dt.month
    expense_df.loc[expense_df['month'] == 12, 'amount'] *= 1.3  # End-of-year expenses
    
    return income_df, expense_df, inventory_df, cash_flow_df

def process_data(income_df, expense_df, inventory_df, cash_flow_df):
    """Process data to generate financial summaries"""
    # Process income data
    monthly_income = income_df.groupby([pd.Grouper(key='date', freq='M'), 'category'])['amount'].sum().unstack(fill_value=0)
    total_income = income_df['amount'].sum()
    
    # Process expense data
    monthly_expenses = expense_df.groupby([pd.Grouper(key='date', freq='M'), 'category'])['amount'].sum().unstack(fill_value=0)
    total_expenses = expense_df['amount'].sum()
    
    # Calculate P&L
    monthly_pnl = monthly_income.sum(axis=1) - monthly_expenses.sum(axis=1)
    
    # Process inventory data
    monthly_inventory_value = inventory_df.groupby([pd.Grouper(key='date', freq='M'), 'product'])\
        .apply(lambda x: (x['quantity'] * x['cost_price']).sum()).unstack(fill_value=0)
    total_inventory_value = (inventory_df['quantity'] * inventory_df['cost_price']).sum()
    
    # Process cash flow data
    monthly_cash_flow = cash_flow_df.groupby([pd.Grouper(key='date', freq='M'), 'type'])['amount'].sum().unstack(fill_value=0)
    monthly_cash_flow['Net'] = monthly_cash_flow['Inflow'] - monthly_cash_flow['Outflow']
    
    return {
        'monthly_income': monthly_income,
        'total_income': total_income,
        'monthly_expenses': monthly_expenses,
        'total_expenses': total_expenses,
        'monthly_pnl': monthly_pnl,
        'monthly_inventory_value': monthly_inventory_value,
        'total_inventory_value': total_inventory_value,
        'monthly_cash_flow': monthly_cash_flow
    }

def generate_charts(data):
    """Generate visualizations for financial reports"""
    charts = {}
    
    # Income by category
    fig, ax = plt.subplots(figsize=(10, 6))
    data['monthly_income'].plot(kind='bar', stacked=True, ax=ax)
    ax.set_title('Monthly Income by Category')
    ax.set_xlabel('Month')
    ax.set_ylabel('Amount ($)')
    charts['income_by_category'] = fig
    
    # Expenses by category
    fig, ax = plt.subplots(figsize=(10, 6))
    data['monthly_expenses'].plot(kind='bar', stacked=True, ax=ax)
    ax.set_title('Monthly Expenses by Category')
    ax.set_xlabel('Month')
    ax.set_ylabel('Amount ($)')
    charts['expenses_by_category'] = fig
    
    # P&L over time
    fig, ax = plt.subplots(figsize=(10, 6))
    data['monthly_pnl'].plot(ax=ax)
    ax.set_title('Monthly Profit & Loss')
    ax.set_xlabel('Month')
    ax.set_ylabel('Net Profit ($)')
    charts['pnl_over_time'] = fig
    
    # Inventory value by product
    fig, ax = plt.subplots(figsize=(10, 6))
    data['monthly_inventory_value'].plot(kind='bar', stacked=True, ax=ax)
    ax.set_title('Monthly Inventory Value by Product')
    ax.set_xlabel('Month')
    ax.set_ylabel('Inventory Value ($)')
    charts['inventory_by_product'] = fig
    
    # Cash flow
    fig, ax = plt.subplots(figsize=(10, 6))
    data['monthly_cash_flow'][['Inflow', 'Outflow', 'Net']].plot(ax=ax)
    ax.set_title('Monthly Cash Flow')
    ax.set_xlabel('Month')
    ax.set_ylabel('Amount ($)')
    charts['cash_flow'] = fig
    
    return charts

def generate_pdf_report(data, charts, filename):
    """Generate PDF report (using matplotlib to save charts)"""
    from matplotlib.backends.backend_pdf import PdfPages
    
    with PdfPages(filename) as pdf:
        # Title page
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.text(0.5, 0.5, 'Financial Report',
                fontsize=24, ha='center', va='center')
        ax.text(0.5, 0.4, f"Generated on: {datetime.now().strftime('%Y-%m-%d')}",
                fontsize=12, ha='center', va='center')
        ax.axis('off')
        pdf.savefig(fig)
        plt.close(fig)
        
        # Income by category
        pdf.savefig(charts['income_by_category'])
        plt.close(charts['income_by_category'])
        
        # Expenses by category
        pdf.savefig(charts['expenses_by_category'])
        plt.close(charts['expenses_by_category'])
        
        # P&L over time
        pdf.savefig(charts['pnl_over_time'])
        plt.close(charts['pnl_over_time'])
        
        # Inventory value by product
        pdf.savefig(charts['inventory_by_product'])
        plt.close(charts['inventory_by_product'])
        
        # Cash flow
        pdf.savefig(charts['cash_flow'])
        plt.close(charts['cash_flow'])
        
        # Summary page
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.text(0.5, 0.9, 'Financial Summary',
                fontsize=18, ha='center', va='center')
        
        ax.text(0.1, 0.7, f"Total Income: ${data['total_income']:,.2f}",
                fontsize=14, ha='left', va='center')
        ax.text(0.1, 0.6, f"Total Expenses: ${data['total_expenses']:,.2f}",
                fontsize=14, ha='left', va='center')
        ax.text(0.1, 0.5, f"Net Profit: ${data['total_income'] - data['total_expenses']:,.2f}",
                fontsize=14, ha='left', va='center')
        ax.text(0.1, 0.4, f"Total Inventory Value: ${data['total_inventory_value']:,.2f}",
                fontsize=14, ha='left', va='center')
        
        ax.axis('off')
        pdf.savefig(fig)
        plt.close(fig)

def generate_excel_report(data, filename):
    """Generate Excel report with multiple sheets"""
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        # Write summary sheet
        summary_df = pd.DataFrame({
            'Metric': ['Total Income', 'Total Expenses', 'Net Profit', 'Total Inventory Value'],
            'Amount': [
                data['total_income'],
                data['total_expenses'],
                data['total_income'] - data['total_expenses'],
                data['total_inventory_value']
            ]
        })
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Write income sheet
        data['monthly_income'].to_excel(writer, sheet_name='Income')
        
        # Write expenses sheet
        data['monthly_expenses'].to_excel(writer, sheet_name='Expenses')
        
        # Write P&L sheet
        pnl_df = data['monthly_pnl'].reset_index()
        pnl_df.columns = ['Month', 'Net Profit']
        pnl_df.to_excel(writer, sheet_name='P&L', index=False)
        
        # Write inventory sheet
        data['monthly_inventory_value'].to_excel(writer, sheet_name='Inventory')
        
        # Write cash flow sheet
        data['monthly_cash_flow'].to_excel(writer, sheet_name='Cash Flow')
        
        # Add charts to Excel
        workbook = writer.book
        worksheet = writer.sheets['Summary']
        
        # Add P&L chart
        chart = workbook.add_chart({'type': 'line'})
        chart.add_series({
            'categories': '=P&L!$A$2:$A$13',
            'values': '=P&L!$B$2:$B$13',
            'name': 'Net Profit'
        })
        chart.set_title({'name': 'Monthly Profit & Loss'})
        chart.set_x_axis({'name': 'Month'})
        chart.set_y_axis({'name': 'Net Profit'})
        worksheet.insert_chart('D2', chart)
        
        # Add income chart
        chart = workbook.add_chart({'type': 'column'})
        for col_num, category in enumerate(data['monthly_income'].columns, 2):
            chart.add_series({
                'categories': f'=Income!$A$2:$A$13',
                'values': f'=Income!${chr(65 + col_num)}$2:${chr(65 + col_num)}$13',
                'name': f'=Income!${chr(65 + col_num)}$1'
            })
        chart.set_title({'name': 'Monthly Income by Category'})
        chart.set_x_axis({'name': 'Month'})
        chart.set_y_axis({'name': 'Income'})
        worksheet.insert_chart('D18', chart)

def get_table_download_link(df, filename):
    """Generate a link to download a dataframe as CSV"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download {filename}</a>'

def main():
    st.title("📊 Financial Report Generator")
    
    # Sidebar controls
    with st.sidebar:
        st.header("Options")
        report_type = st.selectbox("Select Report Type", 
                                  ["P&L Statement", 
                                   "Cash Flow Statement", 
                                   "Inventory Report", 
                                   "Complete Financial Report"])
        
        use_sample_data = st.checkbox("Use Sample Data (for demonstration)")
        show_sample_data = st.button("Show Sample Data")
        
        if use_sample_data or show_sample_data:
            st.markdown("---")
            st.header("Sample Data Preview")
            income_df, expense_df, inventory_df, cash_flow_df = generate_data()
            with st.expander("Income Data"):
                st.dataframe(income_df.head(10))
            with st.expander("Expense Data"):
                st.dataframe(expense_df.head(10))
            with st.expander("Inventory Data"):
                st.dataframe(inventory_df.head(10))
            with st.expander("Cash Flow Data"):
                st.dataframe(cash_flow_df.head(10))
        else:
            st.markdown("""
            **Required data format:**
            - Income: date, category, amount
            - Expenses: date, category, amount
            - Inventory: date, product, quantity, cost_price, selling_price
            - Cash Flow: date, type (Inflow/Outflow), category, amount
            """)
            
        st.markdown("---")
        st.header("Instructions")
        st.markdown("""
        1. Upload your financial data files (CSV or Excel)
        2. Select the type of report you want to generate
        3. View the results in the main panel
        4. Download the report in your preferred format
        """)
    
    # Main content
    if not use_sample_data and not show_sample_data:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Data Upload")
            income_file = st.file_uploader("Upload Income Data", type=["csv", "xlsx"])
            expense_file = st.file_uploader("Upload Expense Data", type=["csv", "xlsx"])
            inventory_file = st.file_uploader("Upload Inventory Data", type=["csv", "xlsx"])
            cash_flow_file = st.file_uploader("Upload Cash Flow Data", type=["csv", "xlsx"])
            
            if income_file and expense_file and inventory_file and cash_flow_file:
                try:
                    income_df = pd.read_csv(income_file) if income_file.name.endswith('.csv') else pd.read_excel(income_file)
                    expense_df = pd.read_csv(expense_file) if expense_file.name.endswith('.csv') else pd.read_excel(expense_file)
                    inventory_df = pd.read_csv(inventory_file) if inventory_file.name.endswith('.csv') else pd.read_excel(inventory_file)
                    cash_flow_df = pd.read_csv(cash_flow_file) if cash_flow_file.name.endswith('.csv') else pd.read_excel(cash_flow_file)
                    
                    # Convert date columns to datetime
                    for df in [income_df, expense_df, inventory_df, cash_flow_df]:
                        if 'date' in df.columns:
                            df['date'] = pd.to_datetime(df['date'])
                    
                    st.success("Files uploaded successfully!")
                except Exception as e:
                    st.error(f"Error reading files: {str(e)}")
                    return
            else:
                st.warning("Please upload all required data files")
                return
    
    if use_sample_data or show_sample_data or (income_file and expense_file and inventory_file and cash_flow_file):
        if use_sample_data or show_sample_data:
            income_df, expense_df, inventory_df, cash_flow_df = generate_data()
        
        if st.button("Generate Report"):
            with st.spinner("Processing data..."):
                # Process the data
                financial_data = process_data(income_df, expense_df, inventory_df, cash_flow_df)
                
                # Generate charts
                charts = generate_charts(financial_data)
                
                # Display summary metrics
                st.markdown('<div class="report-header">Financial Summary</div>', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Income", f"${financial_data['total_income']:,.2f}")
                with col2:
                    st.metric("Total Expenses", f"${financial_data['total_expenses']:,.2f}")
                with col3:
                    st.metric("Net Profit", 
                             f"${financial_data['total_income'] - financial_data['total_expenses']:,.2f}", 
                             delta=f"{(financial_data['total_income'] - financial_data['total_expenses']) / financial_data['total_income']:.1%}")
                with col4:
                    st.metric("Total Inventory Value", f"${financial_data['total_inventory_value']:,.2f}")
                
                # Display charts based on selected report type
                if report_type == "P&L Statement":
                    st.markdown('<div class="report-header">Profit & Loss Statement</div>', unsafe_allow_html=True)
                    st.pyplot(charts['pnl_over_time'])
                elif report_type == "Cash Flow Statement":
                    st.markdown('<div class="report-header">Cash Flow Statement</div>', unsafe_allow_html=True)
                    st.pyplot(charts['cash_flow'])
                elif report_type == "Inventory Report":
                    st.markdown('<div class="report-header">Inventory Report</div>', unsafe_allow_html=True)
                    st.pyplot(charts['inventory_by_product'])
                elif report_type == "Complete Financial Report":
                    st.markdown('<div class="report-header">Complete Financial Report</div>', unsafe_allow_html=True)
                    st.pyplot(charts['income_by_category'])
                    st.pyplot(charts['expenses_by_category'])
                    st.pyplot(charts['pnl_over_time'])
                    st.pyplot(charts['inventory_by_product'])
                    st.pyplot(charts['cash_flow'])
                
                # Download options
                st.markdown('<div class="report-header">Download Report</div>', unsafe_allow_html=True)
                
                # Create download links
                excel_filename = f"financial_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
                pdf_filename = f"financial_report_{datetime.now().strftime('%Y%m%d')}.pdf"
                
                # Generate files in temporary directory
                temp_excel = os.path.join(temp_dir.name, excel_filename)
                temp_pdf = os.path.join(temp_dir.name, pdf_filename)
                
                generate_excel_report(financial_data, temp_excel)
                generate_pdf_report(financial_data, charts, temp_pdf)
                
                # Create download links
                with open(temp_excel, "rb") as f:
                    excel_data = f.read()
                excel_b64 = base64.b64encode(excel_data).decode()
                
                with open(temp_pdf, "rb") as f:
                    pdf_data = f.read()
                pdf_b64 = base64.b64encode(pdf_data).decode()
                
                st.markdown(f"""
                <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_b64}" 
                            download="{excel_filename}">
                    Download Excel Report
                </a>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <a href="data:application/pdf;base64,{pdf_b64}" 
                            download="{pdf_filename}">
                    Download PDF Report
                </a>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()