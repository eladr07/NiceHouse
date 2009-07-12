import settings, models
from datetime import datetime, date
from templatetags.management_extras import commaise
import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0

from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Image, Spacer, Frame, Table, PageBreak
from reportlab.platypus.tables import TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import *
from pyfribidi import log2vis
#register Hebrew fonts
pdfmetrics.registerFont(TTFont('David', settings.MEDIA_ROOT + 'fonts/DavidCLM-Medium.ttf'))
pdfmetrics.registerFont(TTFont('David-Bold', settings.MEDIA_ROOT + 'fonts/DavidCLM-Bold.ttf'))
pdfmetrics.registerFontFamily('David', normal='David', bold='David-Bold')
#template styles
styleN = ParagraphStyle('normal', fontName='David',fontSize=16, leading=15, alignment=TA_RIGHT)
styleDate = ParagraphStyle('date', fontName='David',fontSize=14, leading=15)
styleSubj = ParagraphStyle('subject', fontName='David',fontSize=16, leading=15, alignment=TA_CENTER)
styleSubTitle = ParagraphStyle('subtitle', fontName='David-Bold', fontSize=15, alignment=TA_CENTER)
saleTableStyle = TableStyle(
                            [('FONTNAME', (0,0), (-1,0), 'David-Bold'),
                             ('FONTNAME', (0,1), (-1,-1), 'David'),
                             ('FONTSIZE', (0,0), (-1,-1), 11),
                             ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                             ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                             ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                             ('LEFTPADDING', (0,0), (-1,-1), 8),
                             ('RIGHTPADDING', (0,0), (-1,-1), 8),
                             ]
                            )
projectTableStyle = TableStyle(
                               [('FONTNAME', (0,0), (-1,0), 'David-Bold'),
                                ('FONTNAME', (0,1), (-1,-1), 'David'),
                                ('FONTSIZE', (0,0), (-1,-1), 12),
                                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                ]
                               )

def clientsPara(str):
    str2=''
    parts = str.strip().split('\r\n')
    parts.reverse()
    for s in parts:
        str2 += log2vis(s)
    return Paragraph(str2, ParagraphStyle('clients', fontName='David', fontSize=10, alignment=TA_CENTER))
def titlePara(str):
    '''
    returns a paragraph containing str with the subject style
    '''
    return Paragraph('<b><u>%s</u></b>' % log2vis(str), styleSubj)
def datePara():
    '''
    returns a paragraph containing date with the date style
    '''
    s = log2vis(u'תאריך : %s' % date.today().strftime('%d/%m/%Y'))
    return Paragraph('%s' % s, styleDate)
def tableCaption():
    return Paragraph(u'<u>%s</u>' % log2vis(u'ולהלן פירוט העסקאות'), 
                     ParagraphStyle(name='tableCaption', fontName='David-Bold', fontSize=15,
                                    alignment=TA_CENTER))
def nhLogo():
    return Image(settings.MEDIA_ROOT + 'images/nh_logo.jpg', 300, 50)
def sigPara():
    s = log2vis('ברגשי כבוד,') + '<br/>'
    s += log2vis('אלי בר-און')
    return Paragraph(s, ParagraphStyle(name='sig', fontName='David-Bold', fontSize=15,
                                       alignment=TA_LEFT))
def nhAddr():
    return Image(settings.MEDIA_ROOT + 'images/nh_addr.jpg', 300, 50)

class MonthDemandWriter:
    @property
    def pages_count(self):
        count = self.demand.get_sales().count()
        if count <= 9:
            return 1
        if count <= 25:
            return 2
        if count <= 40:
            return 3
        return 4
    def __init__(self, demand):
        self.demand = demand
    def toPara(self):
        contact = self.demand.project.demand_contact
        s = log2vis(u'בס"ד') + '<br/><br/>'
        s += '<u>%s</u><br/>' % log2vis(u'לכבוד')
        s += '<b>' + log2vis(u'חברת %s' % contact.company) + '<br/>'
        s += log2vis(u'לידי %s' % unicode(contact)) + '<br/>'
        s += log2vis(u'תפקיד : %s</b>' % contact.role) + '<br/></b>'
        s += log2vis(u'א.ג.נ')
        return Paragraph(s, styleN)
    def addLater(self, canv, doc):
        self.current_page += 1
        frame1 = Frame(50, 30, 150, 40)
        frame1.addFromList([Paragraph(log2vis(u'עמוד %s מתוך %s' % (self.current_page, self.pages_count)), 
                            ParagraphStyle('pages', fontName='David', fontSize=13,))], canv)
        frame2 = Frame(0, 680, 650, 150)
        frame2.addFromList([nhLogo(), datePara()], canv)
        if self.current_page == self.pages_count:
            frame3 = Frame(50, 40, 100, 100)
            frame3.addFromList([sigPara()], canv)
        frame4 = Frame(50, 20, 500, 70)
        frame4.addFromList([nhAddr()], canv)
    def addFirst(self, canv, doc):
        self.current_page = 1
        frame1 = Frame(300, 580, 250, 200)
        frame1.addFromList([self.toPara()], canv)
        frame2 = Frame(0, 680, 650, 150)
        frame2.addFromList([nhLogo(), datePara()], canv)
        frame3 = Frame(50, 30, 150, 40)
        frame3.addFromList([Paragraph(log2vis(u'עמוד %s מתוך %s' % (self.current_page, self.pages_count)), 
                            ParagraphStyle('pages', fontName='David', fontSize=13,))], canv)
        frame4 = Frame(50, 20, 500, 70)
        frame4.addFromList([nhAddr()], canv)        
        if self.pages_count == 1:
            frame5 = Frame(50, 40, 100, 100)
            frame5.addFromList([sigPara()], canv)
    def introPara(self):
        s = log2vis(u'א. רצ"ב פירוט דרישתנו לתשלום בגין %i עסקאות שנחתמו החודש.' %
                    self.demand.get_sales().count()) + '<br/>'
        s += log2vis(u'ב. סה"כ מכירות (%s, %s) - %s ש"ח.' %
                     (self.demand.project.commissions.include_tax and u'כולל מע"מ' or u'לא כולל מע"מ',
                      self.demand.project.commissions.include_lawyer and u'כולל שכ"ט עו"ד' or u'לא כולל שכ"ט עו"ד',
                      commaise(self.demand.get_final_sales_amount()))) + '<br/>'
        s += log2vis(u'ג. עמלתנו (כולל מע"מ) - %s ש"ח (ראה פירוט רצ"ב).' % 
                    commaise(self.demand.get_total_amount())) + '<br/>'
        s += log2vis(u'ד. נא בדיקתכם ואישורכם לתשלום לתאריך %s אודה.' % datetime.now().strftime('31/%m/%Y')) + '<br/>'
        s += log2vis(u'ה. במידה ויש שינוי במחירי הדירות ו\או שינוי אחר') + '<br/>'
        s += log2vis(u'אנא עדכנו אותנו בפקס ו\או בטלפון הרצ"ב על גבי דרישה זו.   ') + '<br/>'
        s += log2vis(u'ו. לנוחיותכם, הדרישה מועברת אליכם גם במייל וגם בפקס.')
        return Paragraph(s, ParagraphStyle(name='into', fontName='David', fontSize=14,
                                           alignment=TA_RIGHT, leading=16))
    def saleFlows(self):
        sales = self.demand.get_sales()
        if sales.count() == 0:
            raise AttributeError()
        headers = [log2vis(u'מס"ד')]
        colWidths = [35]
        contract_num, discount, final, zilber = (False, False, False, False)
        for s in sales:
            if s.contract_num:
                headers.append(log2vis(u"חוזה\nמס'"))
                colWidths.append(40)
                contract_num = True
                break
        headers.extend([log2vis(u'שם הרוכשים'),log2vis(u'ודירה\nבניין'),
                        log2vis(u'מכירה\nתאריך'), log2vis(u'חוזה\nמחיר')])
        colWidths.extend([70, None,None,None])
        if self.demand.project.commissions.c_zilber:
            headers.extend([log2vis(u'עו"ד\nשכ"ט'), log2vis(u'לחישוב\nמחיר')])
            colWidths.extend([None,None])
            zilber = True
        if sales.count() > 0 and (sales[0].discount or sales[0].allowed_discount):
            headers.extend([log2vis(u'ניתן\nהנחה\n%'),log2vis(u'מותר\nהנחה\n%')])
            colWidths.extend([None,None])
            discount = True
        headers.extend([log2vis(u'בסיס\nעמלת\n%'),log2vis(u'בסיס\nעמלת\nשווי')])
        colWidths.extend([None,None])
        if self.demand.project.commissions.b_discount_save_precentage:
            headers.extend([log2vis(u'חסכון\nבונוס\n%'),log2vis(u'חסכון\nבונוס\nשווי'),
                            log2vis(u'סופי\nעמלה\n%'),log2vis(u'סופי\nעמלה\nשווי')])
            colWidths.extend([35,30,None,None])
            final = True
        colWidths.reverse()
        headers.reverse()#reportlab prints columns ltr
        i=1
        next_break = 10
        flows = [tableCaption(), Spacer(0,20)]
        rows = []
        for s in sales:
            row = ['%s-%s' % (self.demand.id, i)]
            if contract_num:
                row.append(s.contract_num)
            row.extend([clientsPara(s.clients), '%s/%s' % (s.house.building.num, s.house.num), s.sale_date.strftime('%d/%m/%y'), commaise(s.price)])
            if zilber:
                lawyer_pay = s.price_include_lawyer and (s.price - s.price_no_lawyer) or s.price * 0.015
                row.extend([commaise(lawyer_pay), commaise(s.price_final)])
            if discount:
                row.extend([s.discount, s.allowed_discount])
            row.extend([s.pc_base, commaise(s.pc_base_worth)])
            if final:
                row.extend([s.pb_dsp, commaise(s.pb_dsp_worth), s.c_final, commaise(s.c_final_worth)])
            row.reverse()#reportlab prints columns ltr
            rows.append(row)
            if i % next_break == 0 or i == sales.count():
                if i == sales.count():# insert column summaries
                    if contract_num:
                        row = [None,None,None,log2vis('סה"כ %s' % self.demand.get_sales().count()),None]
                    else:
                        row = [None,None,log2vis('סה"כ %s' % self.demand.get_sales().count()),None]
                    row.append(commaise(self.demand.get_sales_amount()))
                    if zilber:
                        row.extend([None,None])
                    if discount:
                        row.extend([None,None])
                    if final:
                        row.extend([None,None,None,None,None,commaise(self.demand.get_sales_commission())])
                    else:
                        row.extend([None,commaise(self.demand.get_sales_commission())])
                    row.reverse()
                    rows.append(row)
                data = [headers]
                data.extend(rows)
                t = Table(data, colWidths)
                t.setStyle(saleTableStyle)
                flows.append(t)
                if i < sales.count():
                    flows.extend([PageBreak(), Spacer(0,70)])
                    next_break += 15
                rows = []
            i+=1
        return flows
    def remarkPara(self):
        s = '<b><u>%s</u></b><br/>' % log2vis(u'הערות לדרישה')
        remarks = self.demand.remarks.lstrip().rstrip()
        if remarks != None and len(remarks)>0:
            s += log2vis(remarks)
        else:
            s += log2vis(u'אין')
        return Paragraph(s, ParagraphStyle(name='remarkPara', fontName='David', fontSize=13, 
                                           leading=16, alignment=TA_RIGHT))
    def addsPara(self):
        s = ''#'<b><u>%s</u></b><br/>' % log2vis(u'תוספות לדרישה')
        if self.demand.fixed_pay:
            s += log2vis(u'%s - %s ש"ח' % (self.demand.fixed_pay_type, commaise(self.demand.fixed_pay))) + '<br/>'
        if self.demand.var_pay:
            s += log2vis(u'%s - %s ש"ח' % (self.demand.var_pay_type, commaise(self.demand.var_pay))) + '<br/>'
        if self.demand.bonus:
            s += log2vis(u'%s - %s ש"ח' % (self.demand.bonus_type, commaise(self.demand.bonus))) + '<br/>'
        s += '<b>%s</b>' % log2vis(u'סה"כ : %s ש"ח' % commaise(self.demand.get_total_amount())) 
        return Paragraph(s, ParagraphStyle(name='addsPara', fontName='David', fontSize=14, 
                                           leading=16, alignment=TA_LEFT))
    def build(self, filename):
        doc = SimpleDocTemplate(filename)
        story = [Spacer(0,100)]
        title = u'הנדון : עמלה לפרויקט %s לחודש %s/%s' % (self.demand.project, 
                                                          self.demand.month, 
                                                          self.demand.year)
        story.append(titlePara(title))
        story.append(Spacer(0, 10))
        subTitle = '<u>%s</u>' % log2vis(u"דרישה מס' %s" % self.demand.id)
        story.append(Paragraph(subTitle, styleSubTitle))
        story.extend([Spacer(0,20), self.introPara(), Spacer(0,20)])
        story.extend(self.saleFlows())
        if self.demand.get_sales().count() == 10:
            story.append(PageBreak())
        if self.demand.fixed_pay or self.demand.var_pay or self.demand.bonus:
            story.extend([Spacer(0, 20), self.addsPara()])
        story.extend([Spacer(0, 20), self.remarkPara()])    
        doc.build(story, self.addFirst, self.addLater)
        return doc.canv

class MonthProjectsWriter:
    def __init__(self, year, month):
        self.year, self.month = (year, month)
    @property
    def pages_count(self):
        return 1
    def addTemplate(self, canv, doc):
        frame2 = Frame(0, 680, 650, 150)
        frame2.addFromList([nhLogo(), datePara()], canv)
        frame3 = Frame(50, 20, 150, 40)
        frame3.addFromList([Paragraph(log2vis(u'עמוד %s מתוך %s' % (self.current_page, self.pages_count)), 
                            ParagraphStyle('pages', fontName='David', fontSize=13,))], canv)
        frame4 = Frame(50, 30, 500, 70)
        frame4.addFromList([nhAddr()], canv)
        self.current_page += 1
    def projectsFlows(self):
        headers = [log2vis(u'שם היזם'), log2vis(u'שם הפרוייקט'), log2vis(u'סה"כ מכירות'),
                   log2vis(u'סה"כ עמלה'), log2vis(u'מס ח-ן'), log2vis(u'סך ח-ן'),
                   log2vis(u'מס צק'), log2vis(u'סך צק')]
        headers.reverse()
        rows = []
        rowHeights = [28]
        for d in models.Demand.objects.filter(year = self.year, month= self.month):
            project_name = d.project.name.count(d.project.city) > 0 and log2vis(d.project.name) or log2vis(u'%s %s' % (d.project.name, d.project.city))
            row = [log2vis(d.project.initiator), project_name, 
                   commaise(d.get_sales_amount()), commaise(d.get_total_amount()),
                   None,None,None,None]
            row.reverse()
            rows.append(row)
            rowHeights.append(28)
        data = [headers]
        data.extend(rows)
        colWidths = [90,140,None,None,None,None,None,None]
        colWidths.reverse()
        t = Table(data, colWidths, rowHeights)
        t.setStyle(projectTableStyle)
        return [t]
    def build(self, filename):
        self.current_page = 1
        doc = SimpleDocTemplate(filename)
        story = [Spacer(0,50)]
        title = u'ריכוז דרישות לפרוייקטים לחודש %s\%s' % (self.year, self.month)
        story.append(titlePara(title))
        story.append(Spacer(0, 10))
        story.extend(self.projectsFlows())
        doc.build(story, self.addTemplate, self.addTemplate)
        return doc.canv