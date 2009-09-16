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
styleSumRow = ParagraphStyle('sumRow', fontName='David-Bold',fontSize=11, leading=15)
styleSubj = ParagraphStyle('subject', fontName='David',fontSize=16, leading=15, alignment=TA_CENTER)
styleSubTitleBold = ParagraphStyle('subtitle', fontName='David-Bold', fontSize=15, alignment=TA_CENTER)
styleSubTitle = ParagraphStyle('subtitle', fontName='David', fontSize=15, alignment=TA_CENTER)
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
def tableCaption(caption=log2vis(u'ולהלן פירוט העסקאות')):
    return Paragraph(u'<u>%s</u>' % caption, 
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

class EmployeeListWriter:
    def __init__(self, employees, nhemployees):
        self.employees = employees
        self.nhemployees = nhemployees
    @property
    def pages_count(self):
        x = len(self.employees) / 17 + 1
        if len(self.employees) % 17 == 0:
            x+=1
        y = len(self.nhemployees) / 17 + 1
        if len(self.nhemployees) % 17 == 0:
            y+=1
        return x+y+1
    def addLater(self, canv, doc):
        self.current_page += 1
        frame1 = Frame(50, 40, 150, 40)
        frame1.addFromList([Paragraph(log2vis(u'עמוד %s מתוך %s' % (self.current_page, self.pages_count)), 
                            ParagraphStyle('pages', fontName='David', fontSize=13,))], canv)
        frame2 = Frame(0, 680, 650, 150)
        frame2.addFromList([nhLogo(), datePara()], canv)
        frame4 = Frame(50, 20, 500, 70)
        frame4.addFromList([nhAddr()], canv)
    def addFirst(self, canv, doc):
        self.current_page = 1
        frame2 = Frame(0, 680, 650, 150)
        frame2.addFromList([nhLogo(), datePara()], canv)
        frame3 = Frame(50, 40, 150, 40)
        frame3.addFromList([Paragraph(log2vis(u'עמוד %s מתוך %s' % (self.current_page, self.pages_count)), 
                            ParagraphStyle('pages', fontName='David', fontSize=13,))], canv)
        frame4 = Frame(50, 20, 500, 70)
        frame4.addFromList([nhAddr()], canv)
    def employeeFlows(self):
        flows=[Paragraph(log2vis(u'נווה העיר - %s עובדים' % len(self.employees)), styleSubTitleBold),
               Spacer(0,10)]
        headers=[]
        for header in [u'מס"ד',u'פרטי\nשם',u'משפחה\nשם',u'טלפון',u'כתובת',
                       u'העסקה\nתחילת',u'העסקה\nסוג',u'פרוייקטים',u'הערות']:
            headers.append(log2vis(header))
        headers.reverse()
        rows=[]
        i, rank_count, rank = (0,0,None)
        for e in self.employees:
            if rank != e.rank:
                row = [log2vis(unicode(e.rank)),None,None,None,None]
                row.reverse()
                rows.append(row)
                rank = e.rank
                rank_count+=1
                i+=1
            row=[e.id, log2vis(e.first_name), log2vis(e.last_name),
                 log2vis(e.phone), log2vis(e.address), log2vis(e.work_start.strftime('%d/%m/%Y')),
                 log2vis(unicode(e.employment_terms.hire_type))]
            projects=''
            for p in e.projects.all():
                projects += log2vis(p.name) + '\n'
            row.extend([projects, log2vis(e.remarks)])
            row.reverse()
            rows.append(row)
            i+=1
            if i % 17 == 0 or i == len(self.employees) + rank_count:
                data = [headers]
                data.extend(rows)
                t = Table(data)
                t.setStyle(saleTableStyle)
                flows.append(t)
                flows.extend([PageBreak(), Spacer(0,70)])
                rows = []
        flows.extend([Paragraph(log2vis(u'נייס האוס - %s עובדים' % len(self.nhemployees)), styleSubTitleBold),
                      Spacer(0,10)])
        headers=[]
        for header in [u'מס"ד',u'פרטי\nשם',u'משפחה\nשם',u'טלפון',u'כתובת',
                       u'העסקה\nתחילת',u'העסקה\nסוג',u'הערות']:
            headers.append(log2vis(header))
        headers.reverse()
        i, nhbranch_count, nhbranch = (0,0,None)
        for e in self.nhemployees:
            if e.nhbranch != nhbranch:
                row = [log2vis(unicode(e.nhbranch)), None,None,None,None]
                row.reverse()
                rows.append(row)
                nhbranch = e.nhbranch
                nhbranch_count+=1
                i+=1
            row=[e.id, log2vis(e.first_name), log2vis(e.last_name),
                 log2vis(e.phone), log2vis(e.address), log2vis(e.work_start.strftime('%d/%m/%Y')),
                 log2vis(unicode(e.employment_terms and 
                                 e.employment_terms.hire_type or '')), 
                 log2vis(e.remarks)]
            row.reverse()
            rows.append(row)
            i+=1
            if i % 17 == 0 or i == len(self.nhemployees) + nhbranch_count:
                data = [headers]
                data.extend(rows)
                t = Table(data)
                t.setStyle(saleTableStyle)
                flows.append(t)
                if i < len(self.nhemployees) + nhbranch_count:
                    flows.extend([PageBreak(), Spacer(0,70)])
                rows = []        
        return flows
    def build(self, filename):
        doc = SimpleDocTemplate(filename)
        story = [Spacer(0,40)]
        story.append(titlePara(u'מצבת עובדים'))
        story.append(Spacer(0, 10))
        story.extend(self.employeeFlows())
        doc.build(story, self.addFirst, self.addLater)
        return doc.canv

class MonthDemandWriter:
    @property
    def pages_count(self):
        count = self.demand.get_sales().count()
        affected_sales_count = 0
        for subSales in self.demand.get_affected_sales().values():
            affected_sales_count += subSales.count()
        base = self.signup_adds and (affected_sales_count + 17)/17 or 0
        if count <= 9:
            return base + 1
        if count <= 25:
            return base + 2
        if count <= 40:
            return base + 3
        return base + 4
    def __init__(self, demand, to_mail=False):
        if demand.sales.count() == 0:
            raise AttributeError('demand','has no sales')
        self.demand = demand
        self.signup_adds = self.demand.project.commissions.commission_by_signups
        self.to_mail = to_mail
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
        frame1 = Frame(50, 40, 150, 40)
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
        frame3 = Frame(50, 40, 150, 40)
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
    def zilberBonusFlows(self):  
        flows = [tableCaption(caption=log2vis(u'נספח ב - דו"ח חסכון בהנחה')), Spacer(0,20),
                 tableCaption(caption=log2vis(u'מדד בסיס - %s' % self.demand.project.commissions.c_zilber.base_madad)),
                 Spacer(0,30)]
        headers = [log2vis(n) for n in [u'מס"ד', u'שם הרוכשים', u'ודירה\nבניין', u'חוזה\nתאריך',
                                        u'חוזה\nמחיר', u'0 דו"ח\nמחירון', u'חדש\nמדד', 
                                        u'60%\nממודד\nמחירון', u'מחיר\nהפרש', u'בהנחה\nחסכון\nשווי',
                                        u'הערות']]
        headers.reverse()
        rows = []
        i = 1
        total_prices, total_adds = 0, 0
        demand = self.demand
        base_madad = demand.project.commissions.c_zilber.base_madad
        current_madad = demand.get_madad() < base_madad and base_madad or demand.get_madad()
        while demand != None:
            for s in demand.get_sales():
                i += 1
                row = ['%s-%s' % (s.actual_demand.id, i), log2vis(s.clients),'%s/%s' % (s.house.building.num, s.house.num), 
                       s.sale_date.strftime('%d/%m/%y'), commaise(s.price)]
                doh0prices = s.house.versions.filter(type__id = models.PricelistTypeDoh0)
                if doh0prices.count() > 0:
                    doh0price = doh0prices.latest().price
                    memudad = (((current_madad / base_madad) - 1) * 0.6 + 1) * doh0price
                    row.extend([commaise(doh0price), current_madad, commaise(memudad), commaise(s.price-memudad), s.zdb, None])
                    row.reverse()
                rows.append(row)
                total_prices += s.price
                total_adds += s.zdb
                if i % 17 == 0:
                    data = [headers]
                    data.extend(rows)
                    t = Table(data)
                    t.setStyle(saleTableStyle)
                    flows.extend([t, PageBreak(), Spacer(0,70)])
                    rows = []
            if demand.zilber_cycle_index() == 1:
                break
            demand = demand.get_previous_demand()
        sum_row = [None, None, None, None, Paragraph(commaise(total_prices), styleSumRow), None, None, None, None, 
                   Paragraph(commaise(total_adds), styleSumRow), None]
        sum_row.reverse()
        rows.append(sum_row)
        data = [headers]
        data.extend(rows)
        t = Table(data)
        t.setStyle(saleTableStyle)
        flows.append(t)
        return flows
    
    def zilberAddsFlows(self):        
        flows = [tableCaption(caption=log2vis(u'נספח א - הפרשי קצב מכירות לדרישה')),
                 Spacer(0,30)]
        headers = [log2vis(n) for n in [u'דרישה\nחודש', u'שם הרוכשים', u'ודירה\nבניין',u'מכירה\nתאריך', u'חוזה\nמחיר',
                                        u'בדרישה\nעמלה',u'חדשה\nעמלה', u'הפרש\nאחוז', u'בש"ח\nהפרש']]
        
        headers.reverse()
        rows = []
        demand = self.demand
        last_demand_sent = self.demand.get_previous_demand()
        i = 1
        total_prices, total_adds = 0, 0
        while demand != None and demand.zilber_cycle_index() != 1:
            demand = demand.get_previous_demand()
            for s in demand.get_sales():
                row = [log2vis('%s/%s' % (demand.month, demand.year)), clientsPara(s.clients), 
                               '%s/%s' % (s.house.building.num, s.house.num), s.sale_date.strftime('%d/%m/%y'), 
                               commaise(s.price)]
                new_commission = s.c_final
                scd_final = s.project_commission_details.filter(commission='final')[0]
                log = models.ChangeLog.objects.filter(object_type='SaleCommissionDetail',
                                                      object_id=scd_final.id, 
                                                      attribute='value',
                                                      date__lte=last_demand_sent.finish_date)
                orig_commission = log.count() > 0 and float(log.latest().new_value) or new_commission
                if orig_commission == new_commission:
                    continue
                i += 1
                diff_amount = s.price_final * (new_commission - orig_commission) / 100
                row.extend([orig_commission, new_commission, new_commission - orig_commission, commaise(diff_amount)])
                row.reverse()
                rows.append(row)
                total_prices += s.price
                total_adds += diff_amount
                if i % 17 == 0:
                    data = [headers]
                    data.extend(rows)
                    t = Table(data)
                    t.setStyle(saleTableStyle)
                    flows.extend([t, PageBreak(), Spacer(0,70)])
                    rows = []
        sum_row = [None, None, None, None, Paragraph(commaise(total_prices), styleSumRow), None, None, None, 
                   Paragraph(commaise(total_adds), styleSumRow)]
        sum_row.reverse()
        rows.append(sum_row)
        data = [headers]
        data.extend(rows)
        t = Table(data)
        t.setStyle(saleTableStyle)
        flows.append(t)
        return flows
                        
    def signupFlows(self):
        flows = [tableCaption(caption=log2vis(u'להלן תוספות להרשמות מחודשים קודמים')),
                 Spacer(0,30)]
        headers = [log2vis(n) for n in [u'הרשמה\nתאריך',u'דרישה\nחודש', u'הרוכשים\nשם', u'ודירה\nבניין', 
                                        u'חוזה\nתאריך',u'חוזה\nמחיר', u'ששולמה\nעמלה', 
                                        u'חדשה\nעמלה', u'עמלה\nהפרש', u'בש"ח\nהפרש']]
        headers.reverse()
        rows = []
        i = 1
        for subSales in self.demand.get_affected_sales().values():
            for s in subSales.all():
                i += 1
                singup = s.house.get_signup() 
                row = [singup.date.strftime('%d/%m/%y'), s.contractor_pay.strftime('%m/%y'), 
                       clientsPara(s.clients), '%s/%s' % (s.house.building.num, s.house.num), 
                       s.sale_date.strftime('%d/%m/%y'), commaise(s.price)]
                scd_final = s.project_commission_details.filter(commission='final')[0]
                log = models.ChangeLog.objects.filter(object_type='SaleCommissionDetail',
                                                      object_id=scd_final.id, 
                                                      attribute='value',
                                                      date__lt=s.actual_demand.finish_date)
                if log.count() == 0:
                    row.extend([None, s.c_final, s.c_final, commaise(s.c_final_worth)])
                else:
                    paid_final_value = float(log.latest().new_value)
                    diff = s.c_final - paid_final_value
                    row.extend([paid_final_value, s.c_final, 
                                diff, commaise(diff * s.price_final / 100)])
                row.reverse()
                rows.append(row)
                if i % 17 == 0:
                    data = [headers]
                    data.extend(rows)
                    t = Table(data)
                    t.setStyle(saleTableStyle)
                    flows.extend([t, PageBreak(), Spacer(0,70)])
                    rows = []
        sum_row = [None,None,None,None,None,None,None,None,None,Paragraph(commaise(self.demand.bonus), styleSumRow)]
        sum_row.reverse()
        rows.append(sum_row)      
        data = [headers]
        data.extend(rows)
        t = Table(data)
        t.setStyle(saleTableStyle)
        flows.append(t)
        return flows
    def signup_counts_para(self):
        s = log2vis(u'סה"כ הרשמות מצטבר לחישוב עמלה') + '<br/>'
        s += log2vis(u', '.join(u'%s מ - %s/%s' % (count, month[0], month[1]) 
                                for month, count in self.demand.get_signup_months().items())) + '<br/>'
        count = 0
        for subSales in self.demand.get_affected_sales().values():
            count += subSales.count()
        s += log2vis(u' + %s מחודשים קודמים' % count)
        return Paragraph(s, ParagraphStyle('signup_months', fontName='David', fontSize=10, alignment=TA_CENTER))
    def saleFlows(self):
        sales = self.demand.get_sales()
        names = [u'מס"ד']
        colWidths = [35]
        contract_num, discount, final, zilber = (False, False, False, False)
        if sales[0].contract_num:
            names.append(u"חוזה\nמס'")
            colWidths.append(40)
            contract_num = True
        if self.signup_adds:
            names.append(u'הרשמה\nתאריך')
            colWidths.append(None)
        names.extend([u'שם הרוכשים',u'ודירה\nבניין',u'מכירה\nתאריך', u'חוזה\nמחיר'])
        colWidths.extend([70, None,None,None])
        if self.demand.project.is_zilber():
            names.extend([u'מזומן\nהנחת', u'מפרט\nהוצאות',u'עו"ד\nשכ"ט', 
                          u'לחישוב\nמחיר',u'נוספות\nהוצאות'])
            colWidths.extend([35,35,None,None,35])
            zilber = True
	    if not self.demand.project.id == 5:
	        if sales[0].discount or sales[0].allowed_discount:
	            names.extend([u'ניתן\nהנחה\n%',u'מותר\nהנחה\n%'])
	            colWidths.extend([None,None])
	            discount = True
        names.extend([u'בסיס\nעמלת\n%',u'בסיס\nעמלת\nשווי'])
        colWidths.extend([None,None])
        if self.demand.project.commissions.b_discount_save_precentage:
            names.extend([u'חסכון\nבונוס\n%',u'חסכון\nבונוס\nשווי',
                            u'סופי\nעמלה\n%',u'סופי\nעמלה\nשווי'])
            colWidths.extend([35,30,None,None])
            final = True
        colWidths.reverse()
        names.reverse()
        headers = [log2vis(name) for name in names]
        i=1
        next_break = 10
        flows = [tableCaption(), Spacer(0,10)]
        if self.signup_adds:
            flows.extend([self.signup_counts_para(), Spacer(0,10)])
        rows = []
        for s in sales:
            s.restore = True
            row = ['%s-%s' % (self.demand.id, i)]
            if contract_num:
                row.append(s.contract_num)
            if self.signup_adds:
                row.append(s.house.get_signup().date.strftime('%d/%m/%y'))
            row.extend([clientsPara(s.clients), '%s/%s' % (s.house.building.num, s.house.num), s.sale_date.strftime('%d/%m/%y'), commaise(s.price)])
            if zilber:
                lawyer_pay = s.price_include_lawyer and (s.price - s.price_no_lawyer) or s.price * 0.015
                row.extend([None,None,commaise(lawyer_pay), commaise(s.price_final)])
                if s.include_registration == False:
                    row.append(s.house.building.project.commissions.registration_amount)
                else:
                    row.append(None)
            if discount:
                row.extend([s.discount, s.allowed_discount])
            row.extend([s.pc_base, commaise(s.pc_base_worth)])
            if final:
                row.extend([s.pb_dsp, commaise(s.pb_dsp_worth), s.c_final, commaise(s.c_final_worth)])
            row.reverse()#reportlab prints columns ltr
            rows.append(row)
            if i % next_break == 0 or i == sales.count():
                if i == sales.count():# insert column summaries if last row
                    row = [log2vis(u'סה"כ')]
                    if contract_num:
                        row.append(None)
                    if self.signup_adds:
                        row.append(None)
                    row.extend([None,Paragraph(log2vis('%s' % self.demand.get_sales().count()), styleSumRow),None])
                    row.append(Paragraph(commaise(self.demand.get_sales_amount()), styleSumRow))
                    if zilber:
                        row.extend([None,None,None,None,None])
                    if discount:
                        row.extend([None,None])
                    if final:
                        row.extend([None,None,None,None,None,Paragraph(commaise(self.demand.get_sales_commission()), styleSumRow)])
                    else:
                        row.extend([None,Paragraph(commaise(self.demand.get_sales_commission()), styleSumRow)])
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
        remarks = self.demand.remarks
        if remarks != None and len(remarks.lstrip().rstrip())>0:
            s += log2vis(remarks.lstrip().rstrip())
        else:
            s += log2vis(u'אין')
        return Paragraph(s, ParagraphStyle(name='remarkPara', fontName='David', fontSize=13, 
                                           leading=16, alignment=TA_RIGHT))
    def addsPara(self):
        s = ''
        if self.demand.fixed_pay:
            s += log2vis(u'%s - %s ש"ח' % (self.demand.fixed_pay_type, commaise(self.demand.fixed_pay))) + '<br/>'
        if self.demand.var_pay:
            s += log2vis(u'%s - %s ש"ח' % (self.demand.var_pay_type, commaise(self.demand.var_pay))) + '<br/>'
        if self.demand.bonus:
            s += log2vis(u'%s - %s ש"ח' % (self.demand.bonus_type, commaise(self.demand.bonus))) + '<br/>'
        s += '<b>%s</b>' % log2vis(u'סה"כ : %s ש"ח' % commaise(self.demand.get_total_amount())) + '<br/>'
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
        subTitle = u"דרישה מס' %s" % self.demand.id
        if self.demand.project.is_zilber():
            subTitle += u' (%s מתוך %s)' % (self.demand.zilber_cycle_index(), models.ZILBER_CYCLE)

        story.append(Paragraph('<u>%s</u>' % log2vis(subTitle), styleSubTitleBold))
        story.extend([Spacer(0,20), self.introPara(), Spacer(0,20)])
        story.extend(self.saleFlows())
        if self.demand.get_sales().count() == 10:
            story.append(PageBreak())
        if self.demand.fixed_pay or self.demand.var_pay or self.demand.bonus:
            story.extend([Spacer(0, 20), self.addsPara()])
        if self.demand.project.is_zilber():
            story.extend([PageBreak(), Spacer(0,30)])
            story.extend(self.zilberAddsFlows())
            if self.demand.include_zilber_bonus() or not self.to_mail:
                story.extend([PageBreak(), Spacer(0,30)])
                story.extend(self.zilberBonusFlows())
        story.extend([Spacer(0, 20), self.remarkPara()]) 
        if self.signup_adds:
            story.extend([PageBreak(), Spacer(0,30), titlePara(u'נספח א')])
            story.extend(self.signupFlows())
        doc.build(story, self.addFirst, self.addLater)
        return doc.canv

class MultipleDemandWriter:
    def __init__(self, demands, title, show_project, show_month):
        self.demands = demands
        self.title = title
        self.show_month = show_month
        self.show_project = show_project
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
        headers, colWidths = [], []
        if self.show_project:
            headers.extend([log2vis(n) for n in [u'שם היזם', u'שם הפרוייקט']])
            colWidths.extend([90,140])
        if self.show_month:
            headers.append(log2vis(u'חודש'))
            colWidths.append(None)
        headers.extend(log2vis(n) for n in[u'סה"כ מכירות', u'סה"כ עמלה', u'מס ח-ן', u'סך ח-ן', u'מס צק', u'סך צק'])
        headers.reverse()
        colWidths.extend([None,None,None,None,None,None])
        colWidths.reverse()
        rows = []
        rowHeights = [28]
        for d in self.demands:
            row = []
            if self.show_project:
                project_name = d.project.name.count(d.project.city) > 0 and log2vis(d.project.name) or log2vis(u'%s %s' % (d.project.name, d.project.city))
                row.extend([log2vis(d.project.initiator), project_name])
            if self.show_month:
                row.append('%s/%s' % (d.month, d.year))
            row.extend([commaise(d.get_sales_amount()), commaise(d.get_total_amount()), None, None, None, None]) 
            row.reverse()
            rows.append(row)
            rowHeights.append(28)
        data = [headers]
        data.extend(rows)
        t = Table(data, colWidths, rowHeights)
        t.setStyle(projectTableStyle)
        return [t]
    def build(self, filename):
        self.current_page = 1
        doc = SimpleDocTemplate(filename)
        story = [Spacer(0,50)]
        story.append(titlePara(self.title))
        story.append(Spacer(0, 10))
        story.extend(self.projectsFlows())
        doc.build(story, self.addTemplate, self.addTemplate)
        return doc.canv

class EmployeeSalariesWriter:
    def __init__(self, year, month):
        self.year, self.month = (year, month)
        self.salaries = [es for es in models.EmployeeSalary.objects.filter(year = year, month= month)
                         if es.approved_date]
    @property
    def pages_count(self):
        return len(self.salaries) / 28 + 1
    def addTemplate(self, canv, doc):
        frame2 = Frame(0, 680, 650, 150)
        frame2.addFromList([nhLogo(), datePara()], canv)
        frame3 = Frame(50, 20, 150, 40)
        frame3.addFromList([Paragraph(log2vis(u'עמוד %s מתוך %s' % (self.current_page, self.pages_count)), 
                            ParagraphStyle('pages', fontName='David', fontSize=13,))], canv)
        frame4 = Frame(50, 30, 500, 70)
        frame4.addFromList([nhAddr()], canv)
        self.current_page += 1
    def salariesFlows(self):
        flows = []
        headers = [log2vis(u'העובד\nשם'), log2vis(u'סטטוס'), log2vis(u'התלוש\nסכום'),
                   log2vis(u'הצק\nסכום'), log2vis(u'לעובד\nהוצאות\nהחזר'), log2vis(u'מנה"ח\nלחישוב\nברוטו'),
                   log2vis(u'לנטו\nמחושב\nברוטו'), log2vis(u'הערות')]
        headers.reverse()
        colWidths = [None,None,None,None,None,None,None,None]
        colWidths.reverse()
        rows = []
        i = 0
        for es in self.salaries:
            terms = es.employee.employment_terms
            row = [log2vis(unicode(es.employee)), 
                   log2vis(u'%s - %s' % (terms.hire_type.name, terms.salary_net and u'נטו' or u'ברוטו')), 
                   commaise(es.total_amount), commaise(es.check_amount),
                   commaise(es.refund or 0), es.bruto_amount and commaise(es.bruto_amount),
                   None, log2vis(es.remarks or '')]
            row.reverse()
            rows.append(row)
            i += 1
            if i % 27 == 0 or i == len(self.salaries):
                data = [headers]
                data.extend(rows)
                t = Table(data, colWidths)
                t.setStyle(saleTableStyle)
                flows.append(t)
                if i < len(self.salaries):
                    flows.extend([PageBreak(), Spacer(0, 50)])
                rows = []

        return flows
    def build(self, filename):
        self.current_page = 1
        doc = SimpleDocTemplate(filename)
        story = [Spacer(0,50)]
        title = u'שכר עבודה למנהלי פרויקטים לחודש %s\%s' % (self.year, self.month)
        story.append(titlePara(title))
        story.append(Spacer(0, 10))
        story.extend(self.salariesFlows())
        doc.build(story, self.addTemplate, self.addTemplate)
        return doc.canv

class NHEmployeeSalariesWriter:
    def __init__(self, nhmonth, bookkeeping):
        self.bookkeeping = bookkeeping
        self.year, self.month, self.nhbranch = (nhmonth.year, nhmonth.month, nhmonth.nhbranch)
        self.salaries = [nhes for nhes in models.NHEmployeeSalary.objects.filter(year = self.year, month = self.month, 
                                                                                 nhemployee__nhbranch = self.nhbranch)
                                                                                 if nhes.approved_date]
    @property
    def pages_count(self):
        return len(self.salaries) / 28 + 1
    def addTemplate(self, canv, doc):
        frame2 = Frame(0, 680, 650, 150)
        frame2.addFromList([nhLogo(), datePara()], canv)
        frame3 = Frame(50, 20, 150, 40)
        frame3.addFromList([Paragraph(log2vis(u'עמוד %s מתוך %s' % (self.current_page, self.pages_count)), 
                            ParagraphStyle('pages', fontName='David', fontSize=13,))], canv)
        frame4 = Frame(50, 30, 500, 70)
        frame4.addFromList([nhAddr()], canv)
        self.current_page += 1
    def salariesFlows(self):
        flows = []
        headers = [log2vis(n) for n in [u'מס"ד', u'העובד\nשם', u'סטטוס']]
        if self.bookkeeping:
            headers.extend([log2vis(n) for n in [u'התלוש\nסכום', u'הלוואה\nהחזר']])
        headers.append(log2vis(u'הצק\nסכום'))
        if self.bookkeeping:
            headers.extend([log2vis(n) for n in [u'לעובד\nהוצאות\nהחזר',u'מנה"ח\nלחישוב\nברוטו',u'לנטו\nמחושב\nברוטו',u'הערות']])
        headers.reverse()
        colWidths = [None,None,None,None,None,None,None,None]
        colWidths.reverse()
        rows = []
        i = 0
        for es in self.salaries:
            terms = es.nhemployee.employment_terms
            row = [i+1, log2vis(unicode(es.nhemployee)), log2vis(u'%s - %s' % (terms.hire_type.name, terms.salary_net and u'נטו' or u'ברוטו'))]
            if self.bookkeeping:
                row.extend([commaise(es.total_amount), commaise(es.loan_pay)])
            row.append(commaise(es.check_amount))
            if self.bookkeeping:
                row.extend([commaise(es.refund or 0), es.bruto_amount and commaise(es.bruto_amount), None, log2vis(es.remarks or '')])
            row.reverse()
            rows.append(row)
            i += 1
            if i % 27 == 0 or i == len(self.salaries):
                data = [headers]
                data.extend(rows)
                t = Table(data, colWidths)
                t.setStyle(saleTableStyle)
                flows.append(t)
                if i < len(self.salaries):
                    flows.extend([PageBreak(), Spacer(0, 50)])
                rows = []

        return flows
    def build(self, filename):
        self.current_page = 1
        doc = SimpleDocTemplate(filename)
        story = [Spacer(0,50)]
        title = u'שכר עבודה לסניף %s לחודש %s\%s' % (self.nhbranch, self.year, self.month)
        story.append(titlePara(title))
        story.append(Spacer(0, 10))
        story.extend(self.salariesFlows())
        doc.build(story, self.addTemplate, self.addTemplate)
        return doc.canv
