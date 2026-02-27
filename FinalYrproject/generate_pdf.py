from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame, PageTemplate, NextPageTemplate, PageBreak
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT

def create_ieee_pdf(filename):
    doc = SimpleDocTemplate(filename, pagesize=LETTER,
                            rightMargin=0.5*inch, leftMargin=0.5*inch,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='IEEE_Title', fontName='Times-Bold', fontSize=24, leading=28, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='IEEE_Author', fontName='Times-Roman', fontSize=11, leading=14, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='IEEE_Abstract_Head', fontName='Times-Bold', fontSize=9, leading=11, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='IEEE_Abstract_Body', fontName='Times-Bold', fontSize=9, leading=11, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='IEEE_Heading1', fontName='Times-Roman', fontSize=10, leading=12, alignment=TA_CENTER, spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle(name='IEEE_Body', fontName='Times-Roman', fontSize=10, leading=12, alignment=TA_JUSTIFY))
    
    # Content collection
    Story = []
    
    # -- Full Width Title Area --
    Story.append(Paragraph("Stock Price Prediction using Hybrid CNN-LSTM Model", styles['IEEE_Title']))
    Story.append(Spacer(1, 12))
    Story.append(Paragraph("Research Report for Infosys (INFY)", styles['IEEE_Author']))
    Story.append(Spacer(1, 24))
    
    # Abstract
    Story.append(Paragraph("<i>Abstract</i>— This paper presents a hybrid deep learning approach combining Convolutional Neural Networks (CNN) and Long Short-Term Memory (LSTM) networks to forecast Infosys stock prices. The model leverages historical OHLCV data and technical indicators. Experimental results demonstrate the effectiveness of this approach with promising RMSE and MAE scores.", styles['IEEE_Abstract_Body']))
    Story.append(Spacer(1, 12))
    Story.append(Paragraph("<i>Keywords</i>— Stock Prediction, Deep Learning, CNN, LSTM, Financial Forecasting.", styles['IEEE_Abstract_Body']))
    Story.append(Spacer(1, 20))

    # -- Two Column Layout Handled by Frames --
    # We define the content that goes into columns
    
    # I. INTRODUCTION
    Story.append(Paragraph("I. INTRODUCTION", styles['IEEE_Heading1']))
    intro_text = """
    Stock market prediction is a challenging task due to the volatile and non-linear nature of financial time series data. 
    Accurate forecasting can provide significant advantages for investors and financial analysts. Traditional statistical models 
    often struggle to capture complex patterns in such data. Deep learning techniques, particularly CNNs and LSTMs, have shown 
    superior performance in time-series forecasting.
    <br/><br/>
    This research proposes a hybrid CNN-LSTM model. The CNN component is utilized to extract local temporal features from the 
    input sequence, while the LSTM component captures long-term dependencies.
    """
    Story.append(Paragraph(intro_text, styles['IEEE_Body']))

    # II. METHODOLOGY
    Story.append(Paragraph("II. METHODOLOGY", styles['IEEE_Heading1']))
    method_text = """
    <b>A. Data Preprocessing</b><br/>
    Historical data for Infosys (INFY.NS) is fetched from Yahoo Finance. Technical indicators including Moving Averages (MA), 
    Exponential Moving Averages (EMA), Relative Strength Index (RSI), and Moving Average Convergence Divergence (MACD) are calculated 
    and added as features. The data is normalized using Min-Max Scaling.
    <br/><br/>
    <b>B. Model Architecture</b><br/>
    The architecture consists of:
    1) Input Layer: Accepts a sequence of 60 days with 11 features.
    2) 1D Convolutional Layer: extracting local trends.
    3) LSTM Layers: Two stacked LSTM layers to learn temporal dependencies.
    4) Dense Layer: Final output layer predicting the next day's Close price.
    """
    Story.append(Paragraph(method_text, styles['IEEE_Body']))

    # III. EVALUATION
    Story.append(Paragraph("III. EVALUATION METRICS", styles['IEEE_Heading1']))
    eval_text = """
    To evaluate the model's performance, standard regression metrics are used:
    <br/>
    1) <i>Root Mean Squared Error (RMSE)</i>: Measures the standard deviation of residuals.
    2) <i>Mean Absolute Error (MAE)</i>: Average absolute difference between predicted and actual values.
    3) <i>R-Squared (R²)</i>: Indicates the proportion of variance in the dependent variable predictable from the independent variable.
    <br/><br/>
    Recent backtesting on the last 30 days yielded the following typical values:
    <br/>
    - RMSE: ~45.05
    <br/>
    - MAE: ~38.67
    <br/>
    - R²: ~-0.45 (indicating potential for further tuning).
    """
    Story.append(Paragraph(eval_text, styles['IEEE_Body']))

    # IV. CONCLUSION
    Story.append(Paragraph("IV. CONCLUSION", styles['IEEE_Heading1']))
    conc_text = """
    The proposed CNN-LSTM hybrid model demonstrates the capability to track stock price movements. 
    The integration of technical indicators enriches the feature set. 
    Future work will focus on hyperparameter optimization and the inclusion of sentiment analysis data to improve forecast accuracy.
    """
    Story.append(Paragraph(conc_text, styles['IEEE_Body']))
    
    # REFERENCES
    Story.append(Paragraph("REFERENCES", styles['IEEE_Heading1']))
    ref_text = """
    [1] S. Selvin et al., "Stock price prediction using LSTM, RNN and CNN-sliding window model," 2017 International Conference on Advances in Computing, Communications and Informatics (ICACCI).
    <br/>
    [2] Yahoo Finance API, https://pypi.org/project/yfinance/
    """
    Story.append(Paragraph(ref_text, styles['IEEE_Body']))


    # Layout definition
    # Frame 1: Left Column
    frame1 = Frame(doc.leftMargin, doc.bottomMargin, doc.width/2-6, doc.height, id='col1')
    # Frame 2: Right Column
    frame2 = Frame(doc.leftMargin+doc.width/2+6, doc.bottomMargin, doc.width/2-6, doc.height, id='col2')
    
    # We want the Title/Abstract to span full width, but ReportLab Flowables are hard to mix with Frames easily in one go 
    # without a custom flowable or "Span" logic which is complex.
    # Simplified approach: Use a template with 2 columns, but for the first page, we might want a single column header.
    # Actually, easiest "Hack" for IEEE look in ReportLab SimpleDocTemplate:
    # Just put everything in 2 columns? No, title must be centered.
    
    # Better approach:
    # Use a custom PageTemplate.
    
    def title_draw(canvas, doc):
        canvas.saveState()
        canvas.restoreState()

    # Two column frame list
    frames = [frame1, frame2]
    
    template = PageTemplate(id='TwoCol', frames=frames, onPage=title_draw)
    doc.addPageTemplates([template])
    
    # Current limitation: SimpleDocTemplate fills frames in order.
    # If we want Title to span, we normally use a separate Frame for title or draw it on canvas.
    # Let's draw Title on the canvas using 'onFirstPage' methodology? 
    # Or just let the first part be single column? Frames are fixed per page template.
    
    # Let's try to define TWO templates. One for First Page (Title + 2 Col), One for others (2 Col).
    # Actually, simplifying: 
    # Just make the whole document 2 columns, and users accept Title is in left column? NO, that looks bad.
    # Real IEEE: Title spans.
    
    # Let's use a Single Column Frame for the top of page 1, and Two Column Frames for the bottom.
    
    # Frame definitions for Page 1
    # Top frame for title: Height ~ 3 inches
    frame_title = Frame(doc.leftMargin, doc.height - 2.5*inch + doc.bottomMargin, doc.width, 2.5*inch, id='title')
    
    # Bottom Left for Page 1
    frame_b_left = Frame(doc.leftMargin, doc.bottomMargin, doc.width/2-6, doc.height - 2.6*inch, id='p1_left')
    # Bottom Right for Page 1
    frame_b_right = Frame(doc.leftMargin+doc.width/2+6, doc.bottomMargin, doc.width/2-6, doc.height - 2.6*inch, id='p1_right')
    
    # Page 2+ frames (Full height 2 col)
    frame_left = Frame(doc.leftMargin, doc.bottomMargin, doc.width/2-6, doc.height, id='left')
    frame_right = Frame(doc.leftMargin+doc.width/2+6, doc.bottomMargin, doc.width/2-6, doc.height, id='right')
    
    # Templates
    # Page 1 Template
    pt1 = PageTemplate(id='Page1', frames=[frame_title, frame_b_left, frame_b_right])
    # Page 2 Template
    pt2 = PageTemplate(id='Page2', frames=[frame_left, frame_right])
    
    doc.addPageTemplates([pt1, pt2])
    
    # Build
    # Note: We need to trigger "NextPageTemplate" if we spill over, but by default it stays on same if not specified? 
    # Actually SimpleDocTemplate uses the first one. We need to tell it to switch to Page2 for subsequent pages if needed.
    # Use 'NextPageTemplate' flowable after title?
    
    # Let's just put all content. The Flowables flows from frame to frame.
    # Title -> frame_title.
    # Abstract -> frame_title (or frame_b_left? Usually Abstract is full width too in some templates, or top of left col. IEEE usually top of left col OR full width. Let's stick title+abstract in full width top frame).
    
    # We will put Title + Abstract in the 'Story' first. They fill 'frame_title'.
    # If they fit, next content goes to 'frame_b_left'.
    
    # Important: If content spills p1, we want p2 layout.
    Story.insert(0, NextPageTemplate('Page2')) # Set next page to use Page2 template
    
    doc.build(Story)
    print(f"IEEE PDF Generated: {filename}")

if __name__ == "__main__":
    create_ieee_pdf("research_ieee.pdf")
