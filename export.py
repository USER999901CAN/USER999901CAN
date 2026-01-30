import pandas as pd
from io import BytesIO
from fpdf import FPDF
from datetime import datetime
import re

def export_to_csv(df):
    """Export dataframe to CSV"""
    return df.to_csv(index=False).encode('utf-8')

def export_to_excel(df, inputs):
    """Export dataframe and inputs to Excel with formatting"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write projection data
        df.to_excel(writer, sheet_name='Projection', index=False)
        
        # Write inputs summary
        inputs_df = pd.DataFrame([
            ['Current Age', inputs['current_age']],
            ['Birthdate', inputs['birthdate']],
            ['Retirement Age', inputs['retirement_age']],
            ['Total Investments', f"${inputs['total_investments']:,}"],
            ['Monthly Investments', f"${inputs['monthly_investments']:,}"],
            ['Investment Return Rate', f"{inputs['investment_return']}%"],
            ['Yearly Inflation', f"{inputs['yearly_inflation']}%"],
            ['Retirement Year One Income', f"${inputs['retirement_year_one_income']:,}"],
            ['Age 77 Reduction', f"{inputs['age_77_reduction']}%"],
            ['Age 83 Reduction', f"{inputs['age_83_reduction']}%"],
            ['Pension Start Age', inputs['pension_start_age']],
            ['Monthly Pension', f"${inputs['monthly_pension']:,}"],
            ['Part-Time Income', f"${inputs['part_time_income']:,}"],
            ['Part-Time Until Age', inputs['part_time_end_age']],
        ], columns=['Parameter', 'Value'])
        
        inputs_df.to_excel(writer, sheet_name='Inputs', index=False)
        
        # Format the sheets
        workbook = writer.book
        money_fmt = workbook.add_format({'num_format': '$#,##0'})
        
        worksheet = writer.sheets['Projection']
        worksheet.set_column('B:I', 18, money_fmt)
    
    output.seek(0)
    return output.getvalue()


class RetirementPDF(FPDF):
    """Custom PDF class for retirement planning report"""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        if self.page_no() > 1:
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, 'Canadian Retirement Planning Report', 0, 0, 'L')
            self.cell(0, 10, f'Page {self.page_no()}', 0, 1, 'R')
            self.ln(2)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Generated: {datetime.now().strftime("%B %d, %Y")}', 0, 0, 'C')
    
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(41, 128, 185)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, title, 0, 1, 'L', True)
        self.set_text_color(0, 0, 0)
        self.ln(3)
    
    def section_title(self, title):
        self.set_font('Arial', 'B', 11)
        self.set_text_color(41, 128, 185)
        self.cell(0, 8, title, 0, 1, 'L')
        self.set_text_color(0, 0, 0)
        self.ln(1)
    
    def body_text(self, text, indent=0):
        self.set_font('Arial', '', 10)
        self.set_x(10 + indent)
        self.multi_cell(0, 5, text)
    
    def bullet_point(self, text):
        self.set_font('Arial', '', 10)
        self.set_x(15)
        self.multi_cell(0, 5, f"  {text}")
    
    def key_metric(self, label, value, color='green'):
        self.set_font('Arial', 'B', 10)
        self.cell(60, 6, label + ':', 0, 0)
        self.set_font('Arial', 'B', 10)
        if color == 'green':
            self.set_text_color(0, 128, 0)
        elif color == 'red':
            self.set_text_color(255, 0, 0)
        elif color == 'orange':
            self.set_text_color(255, 140, 0)
        self.cell(0, 6, value, 0, 1)
        self.set_text_color(0, 0, 0)


def clean_text(text):
    """Remove emojis and clean markdown from text"""
    # Remove emojis
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    # Remove markdown
    text = text.replace('###', '').replace('**', '').replace('*', '')
    return text.strip()


def export_to_pdf(df, inputs, results):
    """Export comprehensive retirement planning report to PDF"""
    pdf = RetirementPDF()
    pdf.add_page()
    
    # ========== COVER PAGE ==========
    pdf.set_font('Arial', 'B', 24)
    pdf.ln(30)
    pdf.cell(0, 15, 'Your Retirement Plan', 0, 1, 'C')
    pdf.set_font('Arial', '', 14)
    pdf.cell(0, 10, 'A Comprehensive Financial Roadmap', 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 8, f"Prepared for: Age {inputs['current_age']} Individual", 0, 1, 'C')
    pdf.cell(0, 8, f"Report Date: {datetime.now().strftime('%B %d, %Y')}", 0, 1, 'C')
    
    pdf.ln(40)
    
    # Executive Summary Box
    pdf.set_fill_color(240, 248, 255)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Executive Summary', 0, 1, 'C', True)
    pdf.set_font('Arial', '', 10)
    
    years_to_retirement = inputs['retirement_age'] - inputs['current_age']
    final_balance = results['final_balance']
    
    summary_text = (
        f"This report projects your retirement from age {inputs['current_age']} to 100. "
        f"With {years_to_retirement} years until retirement at age {inputs['retirement_age']}, "
        f"your current ${inputs['total_investments']:,.0f} in investments is projected to grow "
        f"and sustain you through retirement, ending with ${final_balance:,.0f} at age 100."
    )
    
    pdf.set_x(15)
    pdf.multi_cell(180, 6, summary_text, 0, 'L', True)
    
    # ========== CURRENT FINANCIAL SITUATION ==========
    pdf.add_page()
    pdf.chapter_title('1. Your Current Financial Situation')
    
    pdf.section_title('Investment Portfolio')
    pdf.body_text(
        f"You currently have ${inputs['total_investments']:,.0f} invested across various accounts. "
        f"This forms the foundation of your retirement savings."
    )
    pdf.ln(2)
    
    # Account breakdown
    accounts = [
        ('TFSA (Tax-Free Savings)', inputs.get('tfsa', 0)),
        ('RRSP (Registered Retirement)', inputs.get('rrsp', 0)),
        ('Non-Registered (Taxable)', inputs.get('non_registered', 0)),
        ('LIRA (Locked-In Retirement)', inputs.get('lira', 0))
    ]
    
    for account_name, amount in accounts:
        if amount > 0:
            pct = (amount / inputs['total_investments']) * 100
            pdf.bullet_point(f"{account_name}: ${amount:,.0f} ({pct:.1f}%)")
    
    pdf.ln(3)
    
    pdf.section_title('Savings Plan')
    pdf.body_text(
        f"You plan to contribute ${inputs['monthly_investments']:,.0f} per month "
        f"(${inputs['monthly_investments'] * 12:,.0f} annually) until age {inputs['stop_investments_age']}. "
        f"This represents {inputs['stop_investments_age'] - inputs['current_age']} years of additional savings."
    )
    
    pdf.ln(3)
    
    pdf.section_title('Investment Assumptions')
    pdf.bullet_point(f"Expected annual return: {inputs['investment_return']}%")
    pdf.bullet_point(f"Inflation rate: {inputs['yearly_inflation']}%")
    pdf.bullet_point(f"Real return (after inflation): {inputs['investment_return'] - inputs['yearly_inflation']:.1f}%")
    
    # ========== RETIREMENT PLAN ==========
    pdf.add_page()
    pdf.chapter_title('2. Your Retirement Income Plan')
    
    pdf.section_title('Retirement Timeline')
    pdf.body_text(
        f"You plan to retire at age {inputs['retirement_age']}, which is {years_to_retirement} years from now. "
        f"Your retirement will span approximately {100 - inputs['retirement_age']} years."
    )
    
    pdf.ln(3)
    
    pdf.section_title('Income Requirements')
    years_until_retirement = inputs['retirement_age'] - inputs['current_age']
    income_at_retirement = inputs['retirement_year_one_income'] * \
        ((1 + inputs['yearly_inflation'] / 100) ** years_until_retirement)
    
    pdf.body_text(
        f"You need ${inputs['retirement_year_one_income']:,.0f} per month in today's dollars. "
        f"Adjusted for inflation, this will be approximately ${income_at_retirement:,.0f} per month "
        f"when you retire at age {inputs['retirement_age']}."
    )
    
    pdf.ln(2)
    pdf.bullet_point(f"Annual income needed (today's dollars): ${inputs['retirement_year_one_income'] * 12:,.0f}")
    pdf.bullet_point(f"Annual income at retirement: ${income_at_retirement * 12:,.0f}")
    
    if inputs.get('age_77_reduction', 0) > 0:
        pdf.bullet_point(f"Reduced by {inputs['age_77_reduction']}% at age 77 (lower expenses)")
    if inputs.get('age_83_reduction', 0) > 0:
        pdf.bullet_point(f"Further reduced by {inputs['age_83_reduction']}% at age 83")
    
    pdf.ln(3)
    
    pdf.section_title('Income Sources in Retirement')
    
    # Part-time work
    if inputs.get('part_time_income', 0) > 0:
        pdf.body_text(
            f"Part-Time Work (Age {inputs.get('part_time_start_age', inputs['retirement_age'])}-{inputs['part_time_end_age']}): "
            f"${inputs['part_time_income']:,.0f}/month"
        )
        pdf.ln(1)
    
    # Pension
    if inputs.get('monthly_pension', 0) > 0:
        inflation_note = " (indexed to inflation)" if inputs.get('pension_inflation_adjusted') else ""
        pdf.body_text(
            f"Government Pension (Age {inputs['pension_start_age']}+): "
            f"${inputs['monthly_pension']:,.0f}/month{inflation_note}"
        )
        pdf.ln(1)
    
    # Investment withdrawals
    pdf.body_text(
        "Investment Withdrawals: Variable amounts to cover remaining expenses"
    )
    
    # ========== PROJECTION RESULTS ==========
    pdf.add_page()
    pdf.chapter_title('3. Financial Projection Results')
    
    pdf.section_title('Key Outcomes')
    
    pdf.key_metric('Balance at Retirement', f"${df[df['Age'] == inputs['retirement_age']]['Investment Balance End'].values[0]:,.0f}", 'green')
    pdf.key_metric('Final Balance at Age 100', f"${final_balance:,.0f}", 'green' if final_balance > 0 else 'red')
    pdf.key_metric('Total Withdrawn from Investments', f"${results['total_withdrawals']:,.0f}", 'orange')
    pdf.key_metric('Total Pension Received', f"${results['total_pension']:,.0f}", 'green')
    
    pdf.ln(3)
    
    # Sustainability assessment
    pdf.section_title('Plan Sustainability')
    if final_balance > 500000:
        pdf.body_text(
            f"Your plan shows strong sustainability with ${final_balance:,.0f} remaining at age 100. "
            "This provides a significant buffer for unexpected expenses or market downturns."
        )
    elif final_balance > 0:
        pdf.body_text(
            f"Your plan is sustainable with ${final_balance:,.0f} remaining at age 100. "
            "Consider the Monte Carlo analysis to understand how market volatility might affect this outcome."
        )
    else:
        pdf.body_text(
            "WARNING: This projection shows your funds depleting before age 100. "
            "Review the recommendations section carefully and consider adjusting your plan."
        )
    
    # ========== YEAR-BY-YEAR PROJECTION TABLE ==========
    pdf.add_page()
    pdf.chapter_title('4. Year-by-Year Projection')
    
    pdf.body_text(
        "This table shows your financial journey from now through retirement. "
        "Key milestones are highlighted to help you understand how your plan evolves."
    )
    pdf.ln(3)
    
    # Create condensed table - show every 5 years plus key ages
    key_ages = [
        inputs['current_age'],
        inputs['stop_investments_age'],
        inputs['retirement_age'],
        inputs.get('part_time_end_age', 65),
        inputs['pension_start_age'],
        77, 83, 90, 95, 100
    ]
    
    # Filter to key ages and every 5 years
    display_rows = df[
        (df['Age'].isin(key_ages)) | 
        (df['Age'] % 5 == 0)
    ].copy()
    
    # Table header
    pdf.set_font('Arial', 'B', 7)
    pdf.set_fill_color(41, 128, 185)
    pdf.set_text_color(255, 255, 255)
    
    col_widths = [15, 30, 25, 25, 30, 30]
    headers = ['Age', 'Balance Start', 'Contrib', 'Withdraw', 'Income', 'Balance End']
    
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 6, header, 1, 0, 'C', True)
    pdf.ln()
    
    # Table rows
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 7)
    
    for idx, row in display_rows.iterrows():
        # Highlight key ages
        if row['Age'] in key_ages:
            pdf.set_fill_color(240, 248, 255)
            fill = True
        else:
            fill = False
        
        age = str(int(row['Age']))
        balance_start = f"${row['Investment Balance Start']/1000:.0f}K" if row['Investment Balance Start'] < 1000000 else f"${row['Investment Balance Start']/1000000:.1f}M"
        contrib = f"${row['Monthly Investment']:.0f}" if row['Monthly Investment'] > 0 else "-"
        withdraw = f"${row['Investment Withdrawal']:.0f}" if row['Investment Withdrawal'] > 0 else "-"
        income = f"${row['Total Monthly Income']:.0f}" if row['Total Monthly Income'] > 0 else "-"
        balance_end = f"${row['Investment Balance End']/1000:.0f}K" if row['Investment Balance End'] < 1000000 else f"${row['Investment Balance End']/1000000:.1f}M"
        
        pdf.cell(col_widths[0], 5, age, 1, 0, 'C', fill)
        pdf.cell(col_widths[1], 5, balance_start, 1, 0, 'R', fill)
        pdf.cell(col_widths[2], 5, contrib, 1, 0, 'R', fill)
        pdf.cell(col_widths[3], 5, withdraw, 1, 0, 'R', fill)
        pdf.cell(col_widths[4], 5, income, 1, 0, 'R', fill)
        pdf.cell(col_widths[5], 5, balance_end, 1, 0, 'R', fill)
        pdf.ln()
    
    pdf.ln(2)
    pdf.set_font('Arial', 'I', 8)
    pdf.multi_cell(0, 4, 
        "Note: Table shows key ages and every 5 years. 'K' = thousands, 'M' = millions. "
        "Contrib = monthly contribution, Withdraw = monthly withdrawal from investments, "
        "Income = total monthly income from all sources."
    )
    
    # ========== ACTIONABLE ADVICE ==========
    pdf.add_page()
    pdf.chapter_title('5. Actionable Recommendations')
    
    # Parse and format advice
    advice_text = results['advice']
    sections = advice_text.split('###')
    
    for section in sections:
        if not section.strip():
            continue
        
        lines = section.strip().split('\n')
        section_title = clean_text(lines[0])
        
        if section_title:
            pdf.section_title(section_title)
        
        for line in lines[1:]:
            clean_line = clean_text(line)
            if not clean_line:
                continue
            
            if clean_line.startswith('-'):
                pdf.bullet_point(clean_line[1:].strip())
            else:
                pdf.body_text(clean_line)
        
        pdf.ln(2)
    
    # ========== IMPORTANT NOTES ==========
    pdf.add_page()
    pdf.chapter_title('6. Important Considerations')
    
    pdf.section_title('Assumptions and Limitations')
    pdf.body_text(
        "This projection is based on several assumptions that may not reflect actual future conditions:"
    )
    pdf.ln(1)
    
    pdf.bullet_point(f"Constant {inputs['investment_return']}% annual return (markets vary significantly)")
    pdf.bullet_point(f"Steady {inputs['yearly_inflation']}% inflation (actual inflation fluctuates)")
    pdf.bullet_point("No major unexpected expenses (medical, home repairs, etc.)")
    pdf.bullet_point("No changes to tax laws or government benefits")
    pdf.bullet_point("Living to age 100 (actual lifespan varies)")
    
    pdf.ln(3)
    
    pdf.section_title('Recommended Next Steps')
    pdf.bullet_point("Run Monte Carlo simulation to test plan against market volatility")
    pdf.bullet_point("Review and update this plan annually or after major life changes")
    pdf.bullet_point("Consult with a fee-only financial planner for personalized advice")
    pdf.bullet_point("Consider tax optimization strategies with a tax professional")
    pdf.bullet_point("Review estate planning documents (will, power of attorney)")
    pdf.bullet_point("Ensure adequate insurance coverage (life, disability, long-term care)")
    
    pdf.ln(3)
    
    pdf.section_title('Market Volatility Warning')
    pdf.set_fill_color(255, 245, 230)
    pdf.set_x(15)
    pdf.multi_cell(180, 5,
        "IMPORTANT: This projection assumes constant returns. Real markets experience significant "
        "volatility with both gains and losses. A Monte Carlo simulation (available in the app) "
        "tests your plan against 10,000 different market scenarios to provide a more realistic "
        "success probability. We strongly recommend running this analysis.",
        0, 'L', True
    )
    
    # Output PDF
    output = BytesIO()
    pdf_string = pdf.output(dest='S')
    if isinstance(pdf_string, str):
        output.write(pdf_string.encode('latin-1', errors='ignore'))
    else:
        output.write(pdf_string)
    output.seek(0)
    return output.getvalue()

